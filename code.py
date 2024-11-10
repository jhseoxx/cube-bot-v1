# import everything
import telegram
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

global bot
global TOKEN

TOKEN = "TOKEN"
bot = telegram.Bot(token="TOKEN HERE")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

ACTION, LINK, NOTES, SUMMARY = range(4)

async def post_init(application: Application) -> None:
    await application.bot.set_my_commands([('start', 'Starts the bot')])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Request GO/ Split"]]

    await update.message.reply_text(
        "Hi! I am a Toya Cube. "
        "What would you like to do today? \n"
        "If doing requests with this bot, any request without your @/username will be ignored."
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Request GO/ Split"
        ),
    )

    return ACTION


async def link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """asks for link"""
    user = update.message.from_user
    logger.info("Request of %s: %s", user.first_name, update.message.text)
    print(update.message.text)
    await update.message.reply_text(
        "I see! Please send me the link to the item/ site, "
        "so I know what you're looking for. Please feel free to send /cancel if you change your mind.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return LINK

async def notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    global itemlink
    itemlink = update.message.text
    print(itemlink)
    logger.info("User %s sending notes", user.first_name)
    await update.message.reply_text(
        "Please input YOUR USERNAME with any notes and/or additional requests.\n"
        "ie. Splits, Price staggering? \n\n"
        "Please note more details about your request will make it easier for me! \n"
    )

    return NOTES


async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    global detail
    detail =  update.message.text
    print(detail)
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    print(detail)
    print(itemlink)
    await update.message.reply_text(f'''Request stored in the cube. Thank you! Here's the summary of your request:\n\n
Item: {itemlink} \nDetail: {detail}'''
                                    )
    await send(f'''Item: {itemlink} \nDetail: {detail}''',[CHAT ID])
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! When you have something for me please come back!", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

async def send(msg, chat_id, token="TOKEN"):
    bot = telegram.Bot(token=token)
    bot.initialize
    await bot.sendMessage(chat_id=chat_id, text=msg)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    await update.message.reply_text(
    '''HELP!!!!!'''
    )
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token("TOKEN").post_init(post_init).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ACTION: [MessageHandler(filters.Regex("^(Request GO/ Split)$"), link)],
            LINK: [MessageHandler(filters.Entity('url'), notes)],
            NOTES: [MessageHandler(filters.TEXT & (~filters.COMMAND), bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(CommandHandler('help',help))
    application.add_handler(conv_handler)
    application.run_polling(poll_interval=5)

if __name__ == "__main__":
    main()
