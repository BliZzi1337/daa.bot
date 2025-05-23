
import discord
from discord.ext import commands, tasks
import re
from datetime import datetime
import json
import os

class AutoVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.creating_channel = False
        self.cleanup_channels.start()
        self.config = self.load_config()

    def load_config(self):
        config_path = 'data/voice_config.json'
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"🚫 voice_config.json nicht gefunden unter: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_server_config(self, guild_id):
        str_guild_id = str(guild_id)
        if str_guild_id in self.config:
            return self.config[str_guild_id]
        print(f"⚠️ Konfiguration für Server {guild_id} nicht gefunden. Fallback auf 'default'.")
        return self.config["default"]

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if self.creating_channel:
            return

        guild = member.guild
        config = self.get_server_config(guild.id)

        if before and after:
            if before.channel != after.channel or before.self_mute != after.self_mute:
                voice_users = []
                for g in self.bot.guilds:
                    for vc in g.voice_channels:
                        for m in vc.members:
                            is_speaking = False
                            if m.voice and hasattr(m.voice, 'speaking'):
                                is_speaking = bool(m.voice.speaking)
                            voice_users.append({
                                'name': m.display_name,
                                'channel': vc.name,
                                'server': g.name,
                                'avatar_url': str(m.avatar.url) if m.avatar else '',
                                'is_muted': m.voice.self_mute,
                                'is_speaking': is_speaking
                            })
                if hasattr(self.bot, 'websocket_handler'):
                    await self.bot.websocket_handler.broadcast({'voice_users': voice_users})

        if after.channel:
            if after.channel.name.startswith(config["channel_prefix"]) or after.channel.name.startswith(config["private_channel_prefix"]):
                is_private = after.channel.name.startswith(config["private_channel_prefix"])
                await self.manage_channels(guild, is_private)
                if not before.channel:
                    await self.send_log(
                        guild,
                        title="🟢 Channel Beitritt",
                        description=f"ist **{after.channel.name}** beigetreten",
                        member=member
                    )

        if before.channel:
            if before.channel.name.startswith(config["channel_prefix"]) or before.channel.name.startswith(config["private_channel_prefix"]):
                is_private = before.channel.name.startswith(config["private_channel_prefix"])
                await self.manage_channels(guild, is_private)
                if not after.channel:
                    await self.send_log(
                        guild,
                        title="🔴 Channel Verlassen",
                        description=f"hat **{before.channel.name}** verlassen",
                        member=member
                    )
                elif before.channel != after.channel:
                    await self.send_log(
                        guild,
                        title="🔄 Channel Wechsel",
                        description=f"wechselte von **{before.channel.name}** zu **{after.channel.name}**",
                        member=member
                    )

    async def manage_channels(self, guild: discord.Guild, is_private: bool):
        if self.creating_channel:
            return

        config = self.get_server_config(guild.id)
        category = guild.get_channel(config["category_id"])
        if not category:
            return

        prefix = config["private_channel_prefix"] if is_private else config["channel_prefix"]
        base_name = config["private_base_channel_name"] if is_private else config["base_channel_name"]

        channels = sorted([
            c for c in category.voice_channels
            if c.name.startswith(prefix)
        ], key=lambda c: int(re.findall(r'\d+', c.name)[-1]))

        empty_channels = [c for c in channels if len(c.members) == 0]
        target_empty = 1 if is_private else 2

        if len(empty_channels) > target_empty:
            for channel in empty_channels[target_empty:]:
                await channel.delete()

        if len(empty_channels) < target_empty:
            base_channel = next((c for c in channels if c.name == base_name), None)

            if base_channel:
                self.creating_channel = True
                try:
                    if is_private:
                        new_name = f"{prefix}2"
                        base_pos = base_channel.position
                        new_channel = await category.create_voice_channel(
                            name=new_name,
                            overwrites=base_channel.overwrites,
                            user_limit=2,
                            bitrate=96000
                        )
                        await new_channel.edit(position=base_pos + 1)
                    else:
                        next_number = len(channels) + 1
                        new_name = f"{prefix}{next_number}"
                        new_channel = await category.create_voice_channel(
                            name=new_name,
                            overwrites=base_channel.overwrites,
                            user_limit=0,
                            bitrate=96000
                        )
                finally:
                    self.creating_channel = False

    async def send_log(self, guild: discord.Guild, title: str, description: str, member: discord.Member):
        config = self.get_server_config(guild.id)
        channel = guild.get_channel(config["log_channel_id"])
        if channel:
            embed = discord.Embed(title=title, description=description, color=discord.Color.orange())
            embed.set_author(name=member.display_name, icon_url=member.avatar.url)
            embed.timestamp = datetime.utcnow()
            await channel.send(embed=embed)

    @tasks.loop(seconds=30)
    async def cleanup_channels(self):
        for guild in self.bot.guilds:
            await self.manage_channels(guild, is_private=False)
            await self.manage_channels(guild, is_private=True)

    @cleanup_channels.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()

    @commands.command(name="voice_config")
    async def voice_config(self, ctx):
        config = self.get_server_config(ctx.guild.id)
        pretty = json.dumps(config, indent=4, ensure_ascii=False)
        await ctx.send(f"📁 Aktive Konfiguration für diesen Server:\n```json\n{pretty}```")

async def setup(bot):
    await bot.add_cog(AutoVoice(bot))
