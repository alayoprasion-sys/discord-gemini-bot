import os
import discord
from discord.ext import commands
import google.generativeai as genai
from gtts import gTTS

# ڕێکخستنی Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# ڕێکخستنی Discord Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"بۆتەکە چالاک بوو وەک: {bot.user}")

# فەرمانەکانی کۆڵی دەنگی (Voice Commands)
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("هاتمە ناو کۆڵی دەنگی!")
    else:
        await ctx.send("تکایە پێشتر خۆت بچۆ ناو چەناڵێکی دەنگی!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("لە چەناڵی دەنگی دەربووم.")
    else:
        await ctx.send("من لە هیچ چەناڵێکی دەنگی نیم!")

@bot.command()
async def speak(ctx, *, text: str):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("پێشتر بچۆ ناو چەناڵێکی دەنگی!")
            return

    # گۆڕینی دەق بۆ دەنگ
    tts = gTTS(text=text, lang='ar')  # دەتوانیت 'ar' یان 'fa' بەکاربهێنیت
    tts.save("voice.mp3")

    vc = ctx.voice_client
    if vc.is_playing():
        vc.stop()

    vc.play(discord.FFmpegPCMAudio("voice.mp3"))
    await ctx.send(f"خوێندنەوەی دەنگ: {text}")

# وەڵامدانەوەی تێکست بە Gemini
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
