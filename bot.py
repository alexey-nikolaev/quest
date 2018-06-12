from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN='519244432:AAHZ33ieu2GwHI-sOYBGFdWlnyR3Ur_QW-s'
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

def start(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="I'm a bot, please talk to me!"
    )

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

def echo(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text=update.message.text
    )

echo_handler = MessageHandler(Filters.text, echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
