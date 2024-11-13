import os
import re
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events, Button
from googletranslate import Translator
import cutlet
from pinyin import get
from transliterate import translit
from pypinyin import pinyin, Style
from g2p_en import G2p
import nltk

nltk.download('averaged_perceptron_tagger_eng')

load_dotenv()

# Define bot credentials and create the Telegram client
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not API_ID or not API_HASH or not BOT_TOKEN:
    print("Error: Bot credentials not found. Please check your .env file.")
    exit(1)

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Helper functions for language pronunciation and transliteration
def mandarin_english_pronunciation(text):
    pinyin_words = pinyin(text, style=Style.NORMAL, heteronym=False)
    pinyin_english = " ".join([item[0] for item in pinyin_words])
    replacements = {
        "zh": "j", "x": "sh", "q": "ch", "c": "ts", "j": "j", "sh": "sh",
        "ch": "ch", "z": "dz", "ü": "yu", "ang": "ahng", "eng": "uhng",
        "ong": "awng", "ai": "eye", "ao": "ow", "ei": "ay", "ou": "oh",
        "ian": "yen", "in": "een", "un": "wun", "uang": "wong",
        "hao": "how", "ma": "mah"
    }
    for key, value in replacements.items():
        pinyin_english = pinyin_english.replace(key, value)
    return pinyin_english.capitalize()

def greek_english_pronunciation(text):
    transliteration = translit(text, 'el', reversed=True)
    replacements = {
        "geia": "yah", "ti": "tee", "kanete": "kah-neh-teh",
        "kh": "h", "y": "ee", "d": "th", "g": "y"
    }
    for key, value in replacements.items():
        transliteration = transliteration.replace(key, value)
    return transliteration.capitalize()

def japanese_to_romaji(text, style="hepburn", use_foreign_spelling=False):
    katsu = cutlet.Cutlet(style)
    katsu.use_foreign_spelling = use_foreign_spelling
    return katsu.romaji(text)

# Translator function
async def translate_text(text, lang):
    translator = Translator(lang)
    return str(translator(text))

# Start command
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply(
        "Welcome! Send me any text to translate, and I'll show you the available languages to choose from."
)

# Translation process
@bot.on(events.NewMessage)
async def handle_message(event):
    if event.message.text == "/start":
        return

    # Store original text and prompt user to select a language
    bot.original_text = event.message.text
    await event.reply(
        "Select a language to translate into:",
        buttons=[
            [Button.inline("English", b"en"), Button.inline("Spanish", b"es")],
            [Button.inline("Japanese", b"ja"), Button.inline("Mandarin", b"zh")],
            [Button.inline("Greek", b"el")]
        ]
    )

@bot.on(events.CallbackQuery)
async def handle_translation(event):
    lang_code = event.data.decode()
    text = bot.original_text
    
    if lang_code not in ["en", "es", "ja", "zh", "el"]:
        await event.reply("Unknown language selected.")
        return

    # Translate text based on selected language
    try:
        translated_text = await translate_text(text, lang_code)
        
        # Additional processing for specific languages
        if lang_code == "ja":
            romaji = japanese_to_romaji(translated_text)
            response = f"**Japanese Translation:** `{translated_text}`\n\nRomaji: `{romaji}`"
        elif lang_code == "zh":
            mandarin_pinyin = get(translated_text, delimiter=" ", format="strip")
            mandarin_pronunciation = mandarin_english_pronunciation(translated_text)
            response = (
                f"**Mandarin Chinese Translation:** `{translated_text}`\n\n"
                f"**Pinyin:** `{mandarin_pinyin}`\n\n"
                f"**Pronunciation:** `{mandarin_pronunciation}`"
            )
        elif lang_code == "el":
            greek_translit = translit(translated_text, 'el', reversed=True)
            greek_pronunciation = greek_english_pronunciation(translated_text)
            response = (
                f"**Greek Translation:** `{translated_text}`\n\n"
                f"**Transliteration:** `{greek_translit}`\n\n"
                f"**Pronunciation:** `{greek_pronunciation}`"
            )
        else:
            response = f"**Translation:** `{translated_text}`"

        await event.reply(response, parse_mode="Markdown")
    except Exception as e:
        await event.reply(f"An error occurred: {e}")

# Run the bot
print("Bot is listening...")
bot.run_until_disconnected()
