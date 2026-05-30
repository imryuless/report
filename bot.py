import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=".",
    intents=intents,
    help_command=None
)

REPORT_CHANNEL_ID = 1510116397878087812
ALLOWED_ROLE_ID = 1510089258273210390
PING_ROLE_ID = 1510143641132208339


class ReportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Approve",
        style=discord.ButtonStyle.green,
        custom_id="approve_report"
    )
    async def approve_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Você precisa ser administrador para usar esse botão.",
                ephemeral=True
            )
            return

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.green()

        for i, field in enumerate(embed.fields):
            if field.name == "Status":
                embed.set_field_at(
                    i,
                    name="Status",
                    value="✅ Approved",
                    inline=False
                )

        await interaction.message.edit(
            embed=embed,
            view=self
        )

        await interaction.response.send_message(
            "Report aprovado com sucesso.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Deny",
        style=discord.ButtonStyle.red,
        custom_id="deny_report"
    )
    async def deny_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Você precisa ser administrador para usar esse botão.",
                ephemeral=True
            )
            return

        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()

        for i, field in enumerate(embed.fields):
            if field.name == "Status":
                embed.set_field_at(
                    i,
                    name="Status",
                    value="❌ Denied",
                    inline=False
                )

        await interaction.message.edit(
            embed=embed,
            view=self
        )

        await interaction.response.send_message(
            "Report negado com sucesso.",
            ephemeral=True
        )


# sincroniza slash commands
@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} slash commands sincronizados.")
    except Exception as e:
        print(e)

    print(f"Logado como {bot.user}")


# verifica permissão
def can_use_report(interaction: discord.Interaction):

    return (
        interaction.user.guild_permissions.administrator
        or discord.utils.get(
            interaction.user.roles,
            id=ALLOWED_ROLE_ID
        )
    )


@bot.tree.command(
    name="report",
    description="Envia um report para a staff."
)
@app_commands.describe(
    scripter="Nome do jogador reportado",
    media_link="Link do Medal/Streamable/etc",
    attachment="Imagem ou vídeo"
)
async def report(
    interaction: discord.Interaction,
    scripter: str,
    media_link: str = None,
    attachment: discord.Attachment = None
):

    # permissão
    if not can_use_report(interaction):

        await interaction.response.send_message(
            "Você não tem permissão para usar esse comando.",
            ephemeral=True
        )
        return

    file_url = None

    # attachment
    if attachment:
        file_url = attachment.url

    # link
    elif media_link:

        allowed_sites = [
            "medal.tv",
            "streamable.com",
            "cdn.discordapp.com",
            "media.discordapp.net",
            "imgur.com",
            "gyazo.com"
        ]

        if media_link.startswith(("http://", "https://")):

            if any(site in media_link for site in allowed_sites):
                file_url = media_link
            else:
                await interaction.response.send_message(
                    "Link não permitido.",
                    ephemeral=True
                )
                return

        else:
            await interaction.response.send_message(
                "Link inválido.",
                ephemeral=True
            )
            return

    else:

        await interaction.response.send_message(
            "Você precisa enviar uma imagem/vídeo ou link.",
            ephemeral=True
        )
        return

    # resposta pública
    public_embed = discord.Embed(
        title="🚨 User Reported",
        description=f"**{scripter}** has been reported and will be reviewed by the managers.",
        color=discord.Color.orange()
    )

    public_embed.set_footer(
        text=f"Reported by {interaction.user}",
        icon_url=interaction.user.display_avatar.url
    )

    await interaction.response.send_message(
        embed=public_embed
    )

    report_channel = bot.get_channel(REPORT_CHANNEL_ID)

    # embed da staff
    staff_embed = discord.Embed(
        title="New Report",
        color=discord.Color.yellow()
    )

    staff_embed.add_field(
        name="💥 Scripter",
        value=scripter,
        inline=True
    )

    staff_embed.add_field(
        name="🛡️ Staff",
        value=interaction.user.mention,
        inline=True
    )

    staff_embed.add_field(
        name="Status",
        value="⏳ Pending Review",
        inline=False
    )

    # attachment
    if attachment:

        file = await attachment.to_file()

        # imagem
        if (
            attachment.content_type
            and attachment.content_type.startswith("image")
        ):
            staff_embed.set_image(
                url=f"attachment://{attachment.filename}"
            )

        await report_channel.send(
            content=f"||<@&{PING_ROLE_ID}>||",
            embed=staff_embed,
            file=file,
            view=ReportView()
        )

    else:

        # imagem por link
        image_extensions = (
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp"
        )

        if any(
            file_url.lower().endswith(ext)
            for ext in image_extensions
        ):
            staff_embed.set_image(url=file_url)

        await report_channel.send(
            content=f"||<@&{PING_ROLE_ID}>||",
            embed=staff_embed,
            view=ReportView()
        )

        # medal / streamable
        await report_channel.send(file_url)


bot.run(TOKEN)