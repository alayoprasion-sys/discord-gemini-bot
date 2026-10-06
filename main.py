import os
import asyncio
import discord
from discord.ext import commands
import google.generativeai as genai

# ڕێکخستنی API Key
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)
    # بەکارهێنانی مۆدێلی نوێتر و خێراتری Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

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
    
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"بۆتی ژمارە {bot_index + 1} چالاک بوو: {bot.user}")

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        # وەڵامدانەوەی AI بۆ منشن یان f‌ەرمانی !ai
        if bot.user.mentioned_in(message) or message.content.startswith("!ai"):
            if model:
                async with message.channel.typing():
                    try:
                        user_text = message.content.replace(f'<@{bot.user.id}>', '').replace('!ai', '').strip()
                        if not user_text:
                            user_text = "سڵاو"

                        # ناردنی پرسیار بۆ AI
                        response = model.generate_content(user_text)
                        
                        if response.text:
                            await message.reply(response.text)
                        else:
                            await message.reply("هیچ وەڵامێک لە AI وەرنەگیرا.")
                    except Exception as e:
                        print(f"کێشەی Gemini لە بۆتی {bot.user}: {e}")
                        await message.reply("ببووره، کێشەیەک لە پرۆسەی وەڵامدانەوەکەدا ڕوویدا.")
            else:
                await message.reply("کلیل لە GEMINI_API_KEY ڕێکنەخراوە.")

        await bot.process_commands(message)

    @bot.command()
    async def join(ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                try:
                    await channel.connect()
                    await ctx.send(f"🤖 {bot.user.name} هاتە ناو چەناڵی دەنگی!")
                except Exception as e:
                    print(f"کێشە لە چوونەژوورەوە: {e}")
        else:
            await ctx.send("تکایە پێشتر خۆت بچۆ ناو چەناڵێکی دەنگی!")

    @bot.command()
    async def leave(ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()

    return bot

async def main():
    tasks = []
    for i, token in enumerate(TOKENS):
        bot = create_bot(i)
        bots.append(bot)
        tasks.append(bot.start(token))
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
