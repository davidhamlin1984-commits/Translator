import os
import asyncio
import discord
from discord.ext import commands
from deep_translator import GoogleTranslator

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

LANG_FLAGS = {
    "en": "🇬🇧",
    "fr": "🇫🇷",
    "de": "🇩🇪",
    "es": "🇪🇸",
}


async def delete_later(*messages: discord.Message, delay: int = 10) -> None:
    await asyncio.sleep(delay)
    for message in messages:
        try:
            await message.delete()
        except Exception:
            pass


async def handle_translation(ctx: commands.Context, target_lang: str) -> None:
    if ctx.message.reference is None or ctx.message.reference.message_id is None:
        msg = await ctx.reply("Reply to a message first, then use this command.")
        await delete_later(ctx.message, msg)
        return

    try:
        original_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    except discord.NotFound:
        msg = await ctx.reply("I couldn't find the message you replied to.")
        await delete_later(ctx.message, msg)
        return
    except discord.HTTPException:
        msg = await ctx.reply("There was a problem reading the replied message.")
        await delete_later(ctx.message, msg)
        return

    original_text = (original_message.content or "").strip()
    if not original_text:
        msg = await ctx.reply("That message has no text to translate.")
        await delete_later(ctx.message, msg)
        return

    try:
        translated = GoogleTranslator(source="auto", target=target_lang).translate(original_text)
    except Exception as e:
        msg = await ctx.reply(f"Translation failed: `{e}`")
        await delete_later(ctx.message, msg)
        return

    flag = LANG_FLAGS.get(target_lang, "🌐")
    reply = await ctx.reply(f"{flag} {translated}")
    await delete_later(ctx.message, reply)


@bot.command(name="en")
async def translate_en(ctx: commands.Context):
    await handle_translation(ctx, "en")


@bot.command(name="fr")
async def translate_fr(ctx: commands.Context):
    await handle_translation(ctx, "fr")


@bot.command(name="de")
async def translate_de(ctx: commands.Context):
    await handle_translation(ctx, "de")


@bot.command(name="es")
async def translate_es(ctx: commands.Context):
    await handle_translation(ctx, "es")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Reply-command translator bot is ready.")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Set DISCORD_BOT_TOKEN in Railway variables.")
    bot.run(TOKEN)
