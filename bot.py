import os
import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Command sync failed: {e}")

    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Translator bot is ready.")


@app_commands.context_menu(name="Translate to English")
async def translate_to_english(interaction: discord.Interaction, message: discord.Message):
    if not interaction.guild:
        await interaction.response.send_message(
            "Use this inside a server.",
            ephemeral=True,
        )
        return

    content = (message.content or "").strip()
    if not content:
        await interaction.response.send_message(
            "That message has no text to translate.",
            ephemeral=True,
        )
        return

    try:
        translated = GoogleTranslator(source="auto", target="en").translate(content)

        await interaction.response.send_message(
            f"📝 Original: {content}\n🇬🇧 English: {translated}",
            ephemeral=True,
        )
    except Exception as e:
        await interaction.response.send_message(
            f"Translation failed: `{e}`",
            ephemeral=True,
        )


async def setup_hook():
    bot.tree.add_command(translate_to_english)

bot.setup_hook = setup_hook


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Set DISCORD_BOT_TOKEN in Railway variables.")
    bot.run(TOKEN)
