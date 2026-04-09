import os
import discord
from discord.ext import commands
from discord import app_commands
from googletrans import Translator

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

translator = Translator()

# ---------- SLASH COMMAND ----------
@bot.tree.command(name="en", description="Translate a replied message to English")
async def translate_to_english(interaction: discord.Interaction):
    # Must be used in a server
    if not interaction.guild:
        await interaction.response.send_message("Use this in a server.", ephemeral=True)
        return

    # Check if user replied to a message
    if not interaction.channel:
        await interaction.response.send_message("Channel not found.", ephemeral=True)
        return

    # Try to get the referenced message
    reference = interaction.message.reference if interaction.message else None

    if not reference or not reference.message_id:
        await interaction.response.send_message(
            "Please reply to a message and then use `/en`.",
            ephemeral=True
        )
        return

    try:
        message = await interaction.channel.fetch_message(reference.message_id)
    except:
        await interaction.response.send_message(
            "Couldn't find the message you replied to.",
            ephemeral=True
        )
        return

    if not message.content:
        await interaction.response.send_message(
            "That message has no text to translate.",
            ephemeral=True
        )
        return

    try:
        translated = translator.translate(message.content, dest="en")

        await interaction.response.send_message(
            f"🌐 **Original:** {message.content}\n🇬🇧 **English:** {translated.text}",
            ephemeral=True
        )

    except Exception as e:
        await interaction.response.send_message(
            f"Translation failed: `{e}`",
            ephemeral=True
        )


# ---------- READY ----------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")
    print("Translator bot is ready.")


# ---------- RUN ----------
if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Set DISCORD_BOT_TOKEN in Railway variables.")
    bot.run(TOKEN)
