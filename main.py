import telepot
from googletranslate import Translator
import cutlet
from pinyin import get
from transliterate import translit
import re, os
from dotenv import load_dotenv
import time
from pypinyin import pinyin, Style
from g2p_en import G2p
import nltk

# Download the required NLTK data
nltk.download('averaged_perceptron_tagger_eng')

load_dotenv()

def mandarin_english_pronunciation(text):
    pinyin_words = pinyin(text, style=Style.NORMAL, heteronym=False)
    pinyin_english = " ".join([item[0] for item in pinyin_words])

    # Replacement dictionary to approximate Mandarin sounds with English equivalents
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
    
    # Replacement dictionary for English-friendly pronunciation
    replacements = {
        "geia": "yah", "ti": "tee", "kanete": "kah-neh-teh",
        "kh": "h", "y": "ee", "d": "th", "g": "y"
    }
    
    for key, value in replacements.items():
        transliteration = transliteration.replace(key, value)

    return transliteration.capitalize()

# Define a function for Japanese Romaji conversion using cutlet
def japanese_to_romaji(text, style="hepburn", use_foreign_spelling=False):
    katsu = cutlet.Cutlet(style)
    katsu.use_foreign_spelling = use_foreign_spelling
    return katsu.romaji(text)

# Define a function to perform the translation and conversion
def translate_and_convert(text):
    try:
        # Set up translators
        to_english = Translator('en')
        to_spanish = Translator('es')
        to_japanese = Translator('ja')
        to_mandarin = Translator('zh')
        to_greek = Translator('el')

        # Perform translations
        english = str(to_english(text))
        spanish = str(to_spanish(text))
        japanese = str(to_japanese(text))
        mandarin = str(to_mandarin(text))
        greek = str(to_greek(text))

        # Romaji conversion for Japanese
        japanese_romaji = japanese_to_romaji(japanese, style="hepburn", use_foreign_spelling=False)

        # Pinyin conversion for Mandarin Chinese
        mandarin_pinyin = get(mandarin, delimiter=" ", format="strip")
        
        # Remove spaces between numbers in Pinyin output if there are no spaces in input
        if not re.search(r'\d\s\d', text):
            mandarin_pinyin = re.sub(r'(?<=\d) (?=\d)', '', mandarin_pinyin)

        # Greek transliteration
        greek_translit = translit(greek, 'el', reversed=True)

        # English-equivalent pronunciation for Mandarin
        mandarin_pronunciation = mandarin_english_pronunciation(mandarin)

        # English-equivalent pronunciation for Greek
        greek_pronunciation = greek_english_pronunciation(greek)
        
        # Format the result
        result = (
            f"**English**\n`{english}`\n\n"
            f"**Spanish**\n`{spanish}`\n\n"
            f"**Japanese**\n`{japanese}`\nRomaji: `{japanese_romaji}`\n\n"
            f"**Mandarin Chinese**\n`{mandarin}`\nPinyin: `{mandarin_pinyin}`\n"
            f"Pronunciation: `{mandarin_pronunciation}`\n\n"
            f"**Greek**\n`{greek}`\nTransliteration: `{greek_translit}`\nPronunciation: `{greek_pronunciation}`"
        )

        return result
    except Exception as e:
        return f"An error occurred: {e}"

# Define a handler for incoming messages
def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        text = msg['text']
        
        # Check for /start command and send a welcome message
        if text == "/start":
            welcome_message = (
                "Welcome! I'm here to help translate your text into multiple languages "
                "and provide phonetic and transliterated forms for Japanese, Mandarin, and Greek. "
                "Just send me any text, and I'll do the rest!"
            )
            bot.sendMessage(chat_id, welcome_message)
            return
        
        # Ignore other commands
        if text.startswith("/"):
            return
        
        # Process and translate text
        response = translate_and_convert(text)
        try:
            bot.sendMessage(chat_id, response, parse_mode='Markdown')
        except Exception as e:
            print(e)

# Set up the bot with your API token
TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    print("Error: BOT TOKEN not found. Please check your .env file.")
    exit(1)

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)

# Keep the program running efficiently
print("Bot is listening...")
while True:
    pass
