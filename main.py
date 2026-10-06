import os
import asyncio
import discord
from discord.ext import commands
import google.generativeai as genai

# ڕێکخستنی API Keyی Gemini
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

# وەردەگرتنی تۆکینی بۆتەکان لە Variables
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
        # ڕێگریکردن لەوەی بۆتەکە وەڵامی پەیامی بۆتەکانی تر یان خۆی بداتەوە
        if message.author.bot:
            return

        # وەڵامدانەوەی AI کاتێک کەسێک منشنی بۆتەکە دەکات (@Bot) یان بە !ai دەستپێدەکات
        if bot.user.mentioned_in(message) or message.content.startswith("!ai"):
            if model:
                async with message.channel.typing():
                    try:
                        # پاککردنەوەی منشنەکە لە دەقەکە
                        user_text = message.content.replace(f'<@{bot.user.id}>', '').replace('!ai', '').strip()
                        if not user_text:
                            user_text = "سڵاو"

                        # ناردنی پرسیارەکە بۆ AI
                        response = model.generate_content(user_text)
                        await message.reply(response.text)
                    except Exception as e:
                        print(f"کێشە لە وەڵامی AI: {e}")
                        await message.reply("ببوورە، کێشەیەک لە پرۆسەی وەڵامدانەوەکەدا ڕوویدا.")
            else:
                await message.reply("کلیل لە GEMINI_API_KEY لە بەشی Variables زێدە نەکراوە.")

        # بەگەڕخستنی فەرمانەکانی تر وەک !join و !leave
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
