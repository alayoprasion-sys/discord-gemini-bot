import os
import discord
from discord.ext import commands
import google.generativeai as genai

# ڕێکخستنی APIی Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# ڕێکخستنی دیسکۆرد
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"بۆتەکە چالاک بوو وەک: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        prompt = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if prompt:
            async with message.channel.typing():
                try:
                    response = model.generate_content(prompt)
                    await message.reply(response.text)
                except Exception as e:
                    await message.reply("هەڵەیەک ڕوویدا لە وەڵامدانەوەدا.")

    await bot.process_commands(message)

bot.run(os.getenv("DISCORD_TOKEN"))

