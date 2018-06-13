#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import (ReplyKeyboardMarkup, Location)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN='519244432:AAHZ33ieu2GwHI-sOYBGFdWlnyR3Ur_QW-s'
CODE='t0Ry2e94'

story = [u'Вас зовут Даша, вам 26 лет, и вы приехали в Москву из маленького города немного поразвлечься и устроиться на работу. В своем городе вы работали продавщицей в магазинчике на автобусной станции, где брали в основном сигареты, водку, пиво, семечки и жвачку. Вы не собирались посвящать себя работе и карьере, и такая работа идеально подходила для того, чтобы вообще не обращать на нее внимания.', u'В Москву поехали скорее из любопытства. Вы бывали здесь и раньше, но город вас все равно еще пугает обилием людей и скоростью проносящихся мимо машин. Вы неспособны за всем этим уследить, за каждым углом вам мерещится что-то враждебное.  Плотно прижимая сумку к себе,  вы засыпаете в зале ожидания Павелецкого вокзала.', u'Вы всегда много ворочались во сне, вот и теперь проснулись от того, что постепенно сползли на пол.', u'Инстинктивно ощупав себя и все вокруг, вы с ужасом поняли, что сумки с документами и деньгами у вас больше нет. По спине побежала струйка холодного пота.', u'Зря вы приехали в этот жестокий город, такие наивные дуры здесь не выживают. Хотя и вы не так наивны: часть денег вы все-таки спрятали в правом чулке.', u'Вы никогда не надеялись на полицию и вообще кого-либо кроме себя, но сейчас, лихорадочно перебирая в голове возможные варианты, вспоминаете про двоюродную сестру, которая давно живет в Москве. В детстве вы были очень близки, вместе играли в куклы и другие игры, но с годами все больше отдалялись. Однажды вы были у нее в гостях и, кажется, все еще помните адрес. Недолго думая, вы подходите к нелегальному таксисту на площади и называете адрес: Шаболовка, 10.', 'loc::55.723506, 37.610287']

CHOOSING, TYPING_REPLY = range(2)

reply_keyboard = [[u'Далее']]
start_keyboard = [[u'Начать игру']]
final_keyboard = [[u'Закончить игру']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
start_markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True, resize_keyboard=True)
final_markup = ReplyKeyboardMarkup(final_keyboard, one_time_keyboard=True, resize_keyboard=True)


def start(bot, update):
    update.message.reply_text(
        u'Привет! Чтобы начать игру, пожалуйста, отправьте боту код, полученный от организаторов.')

    return TYPING_REPLY


def regular_choice(bot, update, user_data):
    if user_data.get('verified', False):

        step = user_data.get('step', 0)
        if step < len(story):
            storyline = story[step]

            if storyline[:5] == 'loc::':
                lat_lon = storyline[5:].split(', ')
                lat = float(lat_lon[0])
                lon = float(lat_lon[1])
                update.message.reply_location(Location(lon, lat), reply_markup=markup)
            else:
                update.message.reply_text(
                    storyline,
                    reply_markup=markup)

            user_data['step'] = user_data.get('step', 0) + 1
        else:
            storyline = u'Далее текст игры пока не написан. Ждите обновлений!'
            user_data['finished'] = True

            update.message.reply_text(
                storyline,
                reply_markup=final_markup)

        return CHOOSING

    else:
        start(bot, update)


def received_information(bot, update, user_data):
    text = update.message.text
    user_data['code'] = text
    
    if text == CODE:
        user_data['verified'] = True
        update.message.reply_text(u'Спасибо, код подтвержден. Приятной игры!', reply_markup=start_markup)

        return CHOOSING

    else:
        user_data['verified'] = False
        update.message.reply_text(u'Вы ввели {}. Попробуйте еще раз.'.format(user_data['code']))

        return TYPING_REPLY


def done(bot, update, user_data):
    if user_data.get('finished', False):
        user_data.clear()

        return ConversationHandler.END
    else:
        return CHOOSING


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [RegexHandler(u'^(Далее|Начать игру)$',
                                    regular_choice,
                                    pass_user_data=True),
                       ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information,
                                          pass_user_data=True),
                           ],
        },

        fallbacks=[RegexHandler(u'^Закончить игру$', done, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
