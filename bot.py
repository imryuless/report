import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(".", intents=intents, help_command=None)

REPORT_CHANNEL_ID = 1510116397878087812
ALLOWED_ROLE_ID = 1510089258273210390
class ReportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Approve",
        style=discord.ButtonStyle.green,
        custom_id="approve_report"
    )
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):

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
    async def deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):

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


@bot.command()
@commands.has_role(ALLOWED_ROLE_ID)
async def report(ctx, scripter: str, media_link: str = None):

    attachment = None

    
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        file_url = attachment.proxy_url

    
    elif media_link:
        if media_link.startswith("http://") or media_link.startswith("https://"):
            file_url = media_link
        else:
            await ctx.send("Link inválido.")
            return

    else:
        await ctx.send("Você precisa enviar uma imagem/vídeo ou um link.")
        return

    
    await ctx.message.delete()

    
    public_embed = discord.Embed(
        title="🚨 User Reported",
        description=f"**{scripter}** has been reported and will be reviewed by the managers.",
        color=discord.Color.orange()
    )

    public_embed.set_footer(
        text=f"Reported by {ctx.author}",
        icon_url=ctx.author.display_avatar.url
    )

    await ctx.send(embed=public_embed)

    
    report_channel = bot.get_channel(REPORT_CHANNEL_ID)

    
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
        value=ctx.author.mention,
        inline=True
    )

    staff_embed.add_field(
        name="Status",
        value="⏳ Pending Review",
        inline=False
    )

    
    await report_channel.send(
        content="||<@&1510143641132208339> ||",
        embed=staff_embed,
        view=ReportView()
    )

    
    if ctx.message.attachments:
        file = await attachment.to_file()
        await report_channel.send(file=file)

    else:
        await report_channel.send(file_url)

bot.run(TOKEN)