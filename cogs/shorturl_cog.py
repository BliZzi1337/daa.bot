
import discord
from discord.ext import commands
from discord import app_commands
from modules.url_shortener import URLShortener

class ShortURLCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            from modules.url_shortener import URLShortener
            self.url_shortener = URLShortener()
        except Exception as e:
            print(f"❌ URL-Kürzer konnte nicht initialisiert werden: {str(e)}")
            self.url_shortener = None

    @app_commands.command(name="shorturl", description="Erstelle eine gekürzte URL")
    @app_commands.describe(
        url="Die URL, die du kürzen möchtest",
        custom_code="Optionaler eigener Code für die URL (z.B. 'goo' für bot.blizzi1337.de/goo)"
    )
    async def shorturl(self, interaction: discord.Interaction, url: str, custom_code: str = None):
        try:
            if self.url_shortener is None:
                await interaction.response.send_message("❌ URL-Kürzer ist nicht verfügbar.", ephemeral=True)
                return
                
            short_code = self.url_shortener.create_short_url(url, interaction.user.id, custom_code)
            if not short_code:
                await interaction.response.send_message("❌ Fehler beim Erstellen der kurzen URL.", ephemeral=True)
                return
                
            short_url = f"https://bot.blizzi1337.de/{short_code}"
            
            embed = discord.Embed(title="🔗 URL-Kürzer", color=0x3bff8f)
            embed.add_field(name="Original URL", value=url, inline=False)
            embed.add_field(name="Gekürzte URL", value=short_url, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message("❌ Es ist ein Fehler aufgetreten.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ShortURLCog(bot))
