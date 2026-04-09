import os
import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator

# Retrieve the bot token from the environment
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Initialize bot with default intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


async def translate_replied_message(interaction: discord.Interaction, target_lang: str) -> None:
    """Helper function to translate the message that the user replied to.

    Parameters
    ----------
    interaction : discord.Interaction
        The interaction representing the slash command invocation.
    target_lang : str
        Language code to translate the message into (e.g., 'en', 'fr').
    """
    # Ensure the command is used in a guild
    if not interaction.guild:
        await interaction.response.send_message(
            "This command can only be used inside a server.",
            ephemeral=True,
        )
        return

    # Check if the command was invoked from a message context
    if not interaction.channel:
        await interaction.response.send_message(
            "Channel not found.",
            ephemeral=True,
        )
        return

    # Determine the message being replied to
    # Slash commands on replies provide a reference via interaction.message.reference
    reference = interaction.message.reference if interaction.message else None
    if not reference or not reference.message_id:
        await interaction.response.send_message(
            "Please reply to a message before using this command.",
            ephemeral=True,
        )
        return

    try:
        # Fetch the original message from the channel using the reference's message ID
        original_msg = await interaction.channel.fetch_message(reference.message_id)
    except Exception:
        await interaction.response.send_message(
            "I couldn't find the message you replied to.",
            ephemeral=True,
        )
        return

    # Extract the content of the original message
    content = (original_msg.content or "").strip()
    if not content:
        await interaction.response.send_message(
            "The replied message has no text to translate.",
            ephemeral=True,
        )
        return

    # Perform the translation using deep_translator
    try:
        translated_text = GoogleTranslator(source="auto", target=target_lang).translate(content)
    except Exception as e:
        await interaction.response.send_message(
            f"Translation failed: `{e}`",
            ephemeral=True,
        )
        return

    # Map language codes to flag emojis for a nicer display
    flags = {
        "en": "🇬🇧",
        "fr": "🇫🇷",
        "de": "🇩🇪",
        "es": "🇪🇸",
    }
    flag = flags.get(target_lang, "🌐")

    # Send the translated text ephemerally
    await interaction.response.send_message(
        f"{flag} {translated_text}",
        ephemeral=True,
    )


# Define individual slash commands for English, French, German, and Spanish translations
@bot.tree.command(name="en", description="Translate a replied message into English")
async def translate_en(interaction: discord.Interaction):
    await translate_replied_message(interaction, "en")


@bot.tree.command(name="fr", description="Translate a replied message into French")
async def translate_fr(interaction: discord.Interaction):
    await translate_replied_message(interaction, "fr")


@bot.tree.command(name="de", description="Translate a replied message into German")
async def translate_de(interaction: discord.Interaction):
    await translate_replied_message(interaction, "de")


@bot.tree.command(name="es", description="Translate a replied message into Spanish")
async def translate_es(interaction: discord.Interaction):
    await translate_replied_message(interaction, "es")


@bot.event
async def on_ready() -> None:
    """Called when the bot is ready. Synchronizes slash commands."""
    try:
        await bot.tree.sync()
        print(f"Synced {len(bot.tree.get_commands())} command(s)")
    except Exception as e:
        print(f"Command sync failed: {e}")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Translator bot with slash commands is ready.")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Set DISCORD_BOT_TOKEN in your environment before running the bot.")
    bot.run(TOKEN)
