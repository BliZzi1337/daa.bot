
import os
import asyncio
import discord
import datetime
import traceback
from discord.ext import commands
from aiohttp import web
from modules.websocket_handler import WebSocketHandler
from modules.url_shortener import URLShortener

url_shortener = None
start_time = None

TOKEN = os.getenv("DISCORD_TOKEN")

# Discord Intents konfigurieren
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
intents.presences = True  # Aktiviere Presence-Updates

# Bot-Instanz erstellen (nur einmal!)
bot = commands.Bot(command_prefix="!", intents=intents)

# 🔁 Slash-Commands synchronisieren
@bot.event
async def on_ready():
    print("\n🤖 Bot startet...")
    print(f"➡️ Bot: {bot.user} (ID: {bot.user.id})")
    print(f"➡️ Server: {len(bot.guilds)}")
    print("\n🔄 Synchronisiere Slash-Commands...")

    try:
        # Guild Commands für DAA Server synchronisieren
        guild = discord.Object(id=1107964583928418324)
        bot.tree.copy_global_to(guild=guild)
        guild_sync = await bot.tree.sync(guild=guild)

        # Globale Commands synchronisieren
        print("Debug: Synchronisiere global...")
        synced = await bot.tree.sync()

        print(f"\n✨ SLASH-COMMANDS ERFOLGREICH SYNCHRONISIERT:")
        print(f"➡️ Guild Commands: {len(guild_sync)}")
        print(f"➡️ Global Commands: {len(synced)}")
        print(f"\n🤖 Bot ist erfolgreich eingeloggt als {bot.user}")
        print(f"🌐 In {len(bot.guilds)} Server(n)")
        print(f"📊 Latenz: {round(bot.latency * 1000)}ms\n")

    except Exception as e:
        print(f"❌ Fehler beim Command-Sync:")
        print(f"➡️ {str(e)}")
        print(f"➡️ {traceback.format_exc()}")

# 🔌 Lade alle Cogs aus dem /cogs Verzeichnis
async def load_all_cogs():
    for file in os.listdir("cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            modulename = file[:-3]
            try:
                await bot.load_extension(f"cogs.{modulename}")
                print(f"✅ Geladen: cogs.{modulename}")
            except Exception as e:
                print(f"❌ Fehler beim Laden von cogs.{modulename}: {e}")

# ⚙️ Lade alle Module aus /modules (nur die mit setup)
async def load_all_modules():
    exclude = ["quiz_manager", "chat_ai"]  # Hilfsmodule ohne setup() hier ausschließen
    for file in os.listdir("modules"):
        if file.endswith(".py") and not file.startswith("_"):
            modulename = file[:-3]
            if modulename in exclude:
                continue
            try:
                await bot.load_extension(f"modules.{modulename}")
                print(f"✅ Geladen: modules.{modulename}")
            except Exception as e:
                print(f"❌ Fehler beim Laden von modules.{modulename}: {e}")

# 🧠 Hauptprogramm-Logik
async def main():
    global start_time
    start_time = datetime.datetime.now(datetime.UTC)

    # Bot initialisieren aber noch nicht starten
    bot.websocket_handler = WebSocketHandler()

    async def health_handler(request):
        bot_name = str(bot.user) if bot.user else "Initialisiere..."
        created_at = bot.user.created_at.strftime('%Y-%m-%d %H:%M:%S') if bot.user else "Nicht verfügbar"
        guild_count = len(bot.guilds) if bot.is_ready() else 0
        status = "Online" if bot.is_ready() else "Initialisiere"

        # Online-Statistiken für bestimmten Server abrufen (ohne Bots)
        target_guild_id = 1335923619242577971
        online_count = 0
        if bot.is_ready():
            guild = bot.get_guild(target_guild_id)
            if guild:
                for member in guild.members:
                    status = getattr(member, 'status', discord.Status.offline)
                    if not member.bot and status != discord.Status.offline:
                        online_count += 1

        # Aktive Voice-Nutzer sammeln
        voice_users = []
        if bot.is_ready():
            for guild in bot.guilds:
                for vc in guild.voice_channels:
                    for member in vc.members:
                        voice_users.append({
                            'name': member.display_name,
                            'channel': vc.name,
                            'server': guild.name,
                            'avatar_url': str(member.avatar.url) if member.avatar else '',
                            'is_muted': member.voice.self_mute
                        })

        # Uptime berechnen
        if start_time:
            now = datetime.datetime.now(datetime.UTC)
            uptime = now - start_time
            days = uptime.days
            hours = uptime.seconds // 3600
            minutes = (uptime.seconds % 3600) // 60
            uptime_str = f"{days} Tage, {hours} Stunden, {minutes} Minuten"
        else:
            uptime_str = "Initialisiere..."

        def get_quiz_leaderboard_html():
            # Quiz-Manager initialisieren
            from modules.quiz_manager import QuizManager
            manager = QuizManager()

            # Statistiken sammeln
            stats = []
            with manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT user_id, 
                               SUM(richtig) as total_correct,
                               SUM(gesamt) as total_questions
                        FROM quiz_progress
                        GROUP BY user_id
                        HAVING SUM(gesamt) > 0
                    """)
                    for row in cur.fetchall():
                        user_id, total_correct, total_questions = row
                        accuracy = (total_correct / total_questions) * 100
                        stats.append((user_id, total_correct, total_questions, accuracy))

            # Nach Genauigkeit und richtigen Antworten sortieren
            stats.sort(key=lambda x: (x[3], x[1]), reverse=True)

            # HTML generieren
            html = []
            for i, (user_id, correct, total, accuracy) in enumerate(stats[:10], 1):
                try:
                    guild = bot.get_guild(1335923619242577971)
                    if guild:
                        member = guild.get_member(int(user_id))
                        username = member.display_name if member else f"User {user_id}"
                    else:
                        user = bot.get_user(int(user_id))
                        username = user.name if user else f"User {user_id}"
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    html.append(f"""
                        <div class="quiz-card">
                            <span class="quiz-medal">{medal}</span>
                            <div class="quiz-info">
                                <span class="quiz-name">{username}</span><br>
                                <span>✅ {correct}/{total} richtig ({accuracy:.1f}%)</span>
                            </div>
                        </div>
                    """)
                except:
                    continue

            return "".join(html) if html else "<div class='quiz-card'>Noch keine Quiz-Ergebnisse verfügbar</div>"

        # Dynamische Inhalte generieren
        voice_users_html = "".join(
            f'<div class="user-card" data-speaking="false">'
            f'<img src="{user.get("avatar_url", "")}" class="user-avatar" onerror="this.style.display=\'none\'"/>'
            f'{"🔇" if user["is_muted"] else "🎙️"}︱🏠 {user["server"]}︱{user["channel"]}︱{user["name"]}'
            f'</div>'
            for user in voice_users
        ) if voice_users else '<p>Keine Nutzer in Voice-Channels</p>'
        quiz_leaderboard_html = get_quiz_leaderboard_html()

        # Template laden und Variablen ersetzen
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            template = f.read()

        status_str = str(status).lower()
        html = template.replace("{status}", str(status))\
            .replace("{status_lower}", status_str)\
            .replace("{bot_name}", bot_name)\
            .replace("{uptime_str}", uptime_str)\
            .replace("{guild_count}", str(guild_count))\
            .replace("{voice_users_html}", voice_users_html)\
            .replace("{quiz_leaderboard_html}", quiz_leaderboard_html)\
            .replace("{online_count}", str(online_count))
        return web.Response(text=html, content_type='text/html')

    # Webserver zuerst einrichten und starten
    # Web-Anwendung mit explizitem Host initialisieren
    app = web.Application()
    async def redirect_handler(request):
        short_code = request.match_info['code']

        try:
            if url_shortener is None:
                print("❌ DEBUG: URL Shortener nicht initialisiert")
                error_msg = "URL Shortener Status: Nicht initialisiert\nGrund: Datenbankverbindung nicht hergestellt"
                return web.Response(text=error_msg, status=503)

            print(f"🔍 DEBUG: Suche URL für Code: {short_code}")
            long_url = url_shortener.get_long_url(short_code)

            if long_url is None:
                print(f"❌ DEBUG: Keine URL gefunden für Code: {short_code}")
                return web.Response(text=f"Fehler: URL nicht gefunden für Code: {short_code}", status=404)

            if long_url:
                if not long_url.startswith(('http://', 'https://')):
                    long_url = 'https://' + long_url
                return web.HTTPFound(long_url)

            error_msg = f"Fehler: URL nicht gefunden\nCode: {short_code}\nStatus: 404"
            return web.Response(text=error_msg, status=404)

        except Exception as e:
            error_msg = f"Fehler: Weiterleitung fehlgeschlagen\nCode: {short_code}\nDetails: {str(e)}\nStatus: 500"
            return web.Response(text=error_msg, status=500)

    app.router.add_get('/', health_handler)
    app.router.add_get('/ws', bot.websocket_handler.handle_connection)
    app.router.add_static('/templates', 'templates')
    app.router.add_get('/{code}', redirect_handler)
    print("✅ Routen erfolgreich konfiguriert")

    # Webserver mit explizitem Host-Binding einrichten
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("Health-Check Server gestartet auf 0.0.0.0:8080")

    async with bot:
        try:
            global url_shortener
            try:
                url_shortener = URLShortener() # URL Shortener einmalig initialisieren
                print("✅ URL Shortener erfolgreich initialisiert")
            except ValueError as e:
                print(f"⚠️ Warnung: URL Shortener deaktiviert - {e}")
                url_shortener = None
            await load_all_modules()
            await load_all_cogs()
            await bot.start(TOKEN)
        finally:
            pass

# 🟢 Bot starten
if __name__ == "__main__":
    bot.websocket_handler = WebSocketHandler()  # WebSocket Handler initialisieren
    asyncio.run(main())
