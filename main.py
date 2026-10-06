import os
import asyncio
import discord
from discord.ext import commands

# دریافت توکن‌ها از Variables (بدون نوشتن مستقیم توکن)
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

# حذف مقادیر خالی
TOKENS = [t for t in TOKENS if t]

bots = []

def create_bot(bot_index):
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"ربات شماره {bot_index + 1} فعال شد: {bot.user}")

    @bot.command()
    async def join(ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                try:
                    await channel.connect()
                    await ctx.send(f"🤖 {bot.user.name} وارد ویس شد!")
                except Exception as e:
                    print(f"خطا در ورود ربات {bot.user}: {e}")
        else:
            await ctx.send("لطفاً ابتدا خودتان وارد یک کانال صوتی شوید!")

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
