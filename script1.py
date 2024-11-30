import asyncio
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, MessageHandler, filters, CommandHandler
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Apply nest_asyncio to allow async inside Jupyter/other nested event loops
nest_asyncio.apply()


# Function to fetch the title of the website
async def get_title(url: str) -> str:
    try:
        # Send a GET request to fetch the page
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                title_tag = soup.find('title')
                title = title_tag.text if title_tag else "No Title 🚫"  # Return "No Title" if no title tag is found
                return title[:40]  # Truncate to 40 characters
    except Exception as e:
        return "No Title 🚫"  # Return "No Title" if there's an error

# Function to validate the URL
def is_valid_url(url: str) -> bool:
    parsed_url = urlparse(url)
    # Check if the URL has either 'http' or 'https' and a valid netloc
    return parsed_url.scheme in ['http', 'https'] and parsed_url.netloc != ''

# Handle the received message
async def handle_message(update: Update, context):
    message = update.message
    text = message.text
    
    # Check if the message contains a URL
    if "http" in text:
        # Extract the first URL from the message (simplified approach)
        url = text.split()[0]
        
        # Validate the URL
        if not is_valid_url(url):
            # Inform the user that the URL is invalid
            await context.bot.send_message(
                chat_id=message.chat.id,
                text="🚫 The URL you provided is not valid. Please make sure it starts with 'http://' or 'https://' and is complete."
            )
            return

        # Ensure the URL starts with 'https://' (Telegram only allows 'https' for web app buttons)
        if url.startswith('http://'):
            # Optionally replace with https://
            url = url.replace('http://', 'https://')

            # Check if the URL is still invalid after modification
            if not is_valid_url(url):
                await context.bot.send_message(
                    chat_id=message.chat.id,
                    text="🚫 The URL you provided is still invalid after updating to 'https://'. Please check the URL."
                )
                return

        # Fetch the website title asynchronously
        title = await get_title(url)
        
        # Create a custom reply keyboard with a button that opens the web app
        reply_keyboard = [
            [
                KeyboardButton(
                    text=f"{title}",  # Button text includes the website title
                    web_app={"url": url}
                )
            ]
        ]
        
        # Create the ReplyKeyboardMarkup
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        
        # Send the message with the reply keyboard first (web app button in keyboard)
        await context.bot.send_message(
            chat_id=message.chat.id,
            text=f"🥳",
            reply_markup=reply_markup
        )
        
        # Create the Inline Keyboard with Web App button
        inline_keyboard = [
            [
                InlineKeyboardButton(
                    text=f"{title}",  # Button text includes the website title
                    web_app={"url": url}
                )
            ]
        ]
        
        # Create InlineKeyboardMarkup
        inline_markup = InlineKeyboardMarkup(inline_keyboard)
        
        # Send the message with the inline button and a clickable link to the website
        await context.bot.send_message(
            chat_id=message.chat.id,
            text=f"Title: {title}\nURL: {url}",  # Markdown link format
            reply_markup=inline_markup,
            parse_mode="Markdown"  # This enables Markdown formatting for the link
        )
    else:
        # If no URL is detected in the message, inform the user
        await context.bot.send_message(
            chat_id=message.chat.id,
            text="❓ Please send a valid URL starting with 'http://' or 'https://'."
        )

# Handle /start command
async def start(update: Update, context):
    await context.bot.send_message(
        chat_id=update.message.chat.id,
        text=(
            "👋 Welcome! Send me any website link and I will create a mini app for it.\n"
            "Just paste a valid URL (starting with 'http://' or 'https://') and I'll generate the app."
        )
    )
