import telepot
from googletranslate import Translator
import cutlet
from pinyin import get
from transliterate import translit
import re

# Define a function for Japanese Romaji conversion using cutlet
def japanese_to_romaji(text, style="hepburn", use_foreign_spelling=False):
    katsu = cutlet.Cutlet(style)
    katsu.use_foreign_spelling = use_foreign_spelling
    return katsu.romaji(text)

# Define a function to perform the translation and conversion
def translate_and_convert(text):
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

    # Check if there are no spaces between numbers in the input text
    if not re.search(r'\d\s\d', text):
        # Remove spaces between numbers in Pinyin output if there are no spaces in input
        mandarin_pinyin = re.sub(r'(?<=\d) (?=\d)', '', mandarin_pinyin)

    # Greek transliteration
    greek_translit = translit(greek, 'el', reversed=True)

    # Format the result
    result = (
        f"**English**\n{english}\n\n"
        f"**Spanish**\n{spanish}\n\n"
        f"**Japanese**\n{japanese}\nRomaji: {japanese_romaji}\n\n"
        f"**Mandarin Chinese**\n{mandarin}\nPinyin: {mandarin_pinyin}\n"
        f"Pronunciation: {mandarin_pinyin} (phonetic)\n\n"
        f"**Greek**\n{greek}\nTransliteration: {greek_translit}\n"
    )

    return result

# Define a handler for incoming messages
def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        text = msg['text']
        response = translate_and_convert(text)
        bot.sendMessage(chat_id, response, parse_mode='Markdown')

# Set up the bot with your API token
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telepot.Bot(TOKEN)
bot.message_loop(handle)

# Keep the program running
print("Bot is listening...")
while True:
    pass
