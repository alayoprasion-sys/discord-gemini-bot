import os
import asyncio
import random
import discord
from discord.ext import commands, tasks
from google import genai

# ڕێکخستنی API Keyی Gemini
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")

if GENAI_API_KEY:
    client = genai.Client(api_key=GENAI_API_KEY)
else:
    client = None

# وەردەگرتنی تۆکینی بۆتەکان
TOKENS = [
    os.getenv("DISCORD_TOKEN_1"),
    os.getenv("DISCORD_TOKEN_2"),
    os.getenv("DISCORD_TOKEN_3"),
    os.getenv("DISCORD_TOKEN_4"),
    os.getenv("DISCORD_TOKEN_5"),
    os.getenv("DISCORD_TOKEN_6"),
    os.getenv("DISCORD_TOKEN_7"),
    os.getenv("DISCORD_TOKEN_8"),
]

TOKENS = [t for t in TOKENS if t]

bots = []

def create_bot(bot_index):
    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    
    bot = commands.Bot(command_prefix="!", intents=intents)

    # تەنها هەندێک لە بۆتەکان بە ئۆتۆماتیکی گۆڕانکارییان بەسەردا دێت
    @tasks.loop(minutes=10)
    async def auto_switch_voice():
        if not bot.guilds:
            return

        # شەنسی ٤٠٪ بۆ هەبوونی گۆڕانکاری لەم بۆتەدا (بۆ ئەوەی تەنها ١ تا ٣ بۆت بجوڵێن)
        if random.random() > 0.4:
            return

        for guild in bot.guilds:
            voice_channels = guild.voice_channels
            if len(voice_channels) < 2:
                continue

            # ئەگەر بۆتەکە لە چەناڵێکی دەنگیدا بێت
            if guild.me.voice and guild.me.voice.channel:
                current_channel = guild.me.voice.channel
                next_channels = [ch for ch in voice_channels if ch != current_channel]
                
                if next_channels:
                    # هەڵبژاردنی چەناڵێکی دەنگی تر بە بەختیارانه (Random)
                    target = random.choice(next_channels)
                    try:
                        await guild.voice_client.move_to(target)
                        print(f"🤖 بۆتی {bot.user.name} ڕاگوێزرا بۆ: {target.name}")
                    except Exception as e:
                        print(f"کێشە لە ڕاگوێزتن: {e}")

    @auto_switch_voice.before_loop
    async def before_auto_switch():
        await bot.wait_until_ready()

    @bot.event
    async def on_ready():
        print(f"بۆتی ژمارە {bot_index + 1} چالاک بوو: {bot.user}")
        if not auto_switch_voice.is_running():
            auto_switch_voice.start()

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        # وەڵامدانەوەی AI
        if bot.user.mentioned_in(message) or message.content.startswith("!ai"):
            if client:
                async with message.channel.typing():
                    user_text = message.content.replace(f'<@{bot.user.id}>', '').replace('!ai', '').strip()
                    if not user_text:
                        user_text = "سڵاو"

                    response_text = None
                    try:
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=user_text,
                        )
                        response_text = response.text
                    except Exception as e1:
                        try:
                            response = client.models.generate_content(
                                model='gemini-1.5-flash',
                                contents=user_text,
                            )
                            response_text = response.text
                        except Exception as e2:
                            print(f"کێشە لە AI: {e2}")

                    if response_text:
                        await message.reply(response_text)
                    else:
                        await message.reply("ببوورە، سێرڤەری AI لەم کاتەدا وەڵام ناداتەوە.")
            else:
                await message.reply("کلیل لە GEMINI_API_KEY ڕێکنەخراوە.")

        await bot.process_commands(message)

    @bot.command()
    async def join(ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            try:
                if ctx.voice_client is not None:
                    await ctx.voice_client.move_to(channel)
                else:
                    await channel.connect()
                await ctx.send(f"🤖 {bot.user.name} هاتە ناو چەناڵی: {channel.name}")
            except Exception as e:
                print(f"کێشە لە جۆینبوون: {e}")
        else:
            await ctx.send("تکایە پێشتر خۆت بچۆ ناو چەناڵێکی دەنگی!")

    @bot.command()
    async def leave(ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send(f"👋 {bot.user.name} دەرچوو.")

    return bot

async def main():
    tasks_list = []
    for i, token in enumerate(TOKENS):
        bot = create_bot(i)
        bots.append(bot)
        tasks_list.append(bot.start(token))
    
    await asyncio.gather(*tasks_list)

if __name__ == "__main__":
    asyncio.run(main())
