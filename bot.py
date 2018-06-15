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

#Отправить локацию: loc::<lat>, <lon>
#Изображение: img::<url>::<caption>
#TALKS Кнопки с вариантами реплик и ответы к ним: tlk::<start>::<opt1>||<opt2>||..4::<response1>||<response2>||..4::<important1>, <important2>...

story = [u'Вас зовут Даша, вам 26 лет, и вы приехали в Москву из маленького города немного поразвлечься и устроиться на работу. В своем городе вы работали продавщицей в магазинчике на автобусной станции, где брали в основном сигареты, водку, пиво, семечки и жвачку. Вы не собирались посвящать себя работе и карьере, и такая работа идеально подходила для того, чтобы вообще не обращать на нее внимания.', u'В Москву поехали скорее из любопытства. Вы бывали здесь и раньше, но город вас все равно еще пугает обилием людей и скоростью проносящихся мимо машин. Вы неспособны за всем этим уследить, за каждым углом вам мерещится что-то враждебное.  Плотно прижимая сумку к себе,  вы засыпаете в зале ожидания Павелецкого вокзала.', u'Вы всегда много ворочались во сне, вот и теперь проснулись от того, что постепенно сползли на пол.', u'Инстинктивно ощупав себя и все вокруг, вы с ужасом поняли, что сумки с документами и деньгами у вас больше нет. По спине побежала струйка холодного пота.', u'Зря вы приехали в этот жестокий город, такие наивные дуры здесь не выживают. Хотя и вы не так наивны: часть денег вы все-таки спрятали в правом чулке.', u'Вы никогда не надеялись на полицию и вообще кого-либо кроме себя, но сейчас, лихорадочно перебирая в голове возможные варианты, вспоминаете про двоюродную сестру, которая давно живет в Москве. В детстве вы были очень близки, вместе играли в куклы и другие игры, но с годами все больше отдалялись. Однажды вы были у нее в гостях и, кажется, все еще помните адрес. Недолго думая, вы подходите к нелегальному таксисту на площади и называете адрес: Шаболовка, 20.', u'loc::55.721544, 37.609568', u'Дом кажется вам странным, каким-то слишком бедным для центра Москвы, как бы застывшем в советском прошлом. Позднее вы узнаете, что это малогабаритная хрущевка, чудом уцелевшая в программе реновации, и живут тут самые обычные люди. Под лавкой у первого подъезда вы замечаете что-то странное.', u'Непонятно, чего это вы полезли под лавку, ну приклеил кто-то туда QR-код и ладно, мало ли о чем люди думают… В таком неприличном виде, кверху задницей, вас и застает одна из местных бабок.', u'img::http://novosti.az/media/2017/12/16/baddi.jpg::Дора', u'tlk::Дора: Что это ты там забыла, милочка? Чай не бомбу закладываешь? Иди лучше куда шла, нам тут такого не надо.::Это не вы туда приклеили? Какой-то код…||Мне негде переночевать. Вы случайно не сдаете комнату?||У меня тут сестра живет, Наташа. Темненькая такая, но русская, высокая. У меня телефон украли, не могу ей позвонить. Не знаете, где она может быть сейчас?||Классный прикид. Где брали?::Я что, по-твоему, совсем из ума выжила? Я бы и не залезла туда. Мальчишки дворовые, наверное, развлекаются.||Ага, чтоб ты меня потом обчистила и дальше свою наркоту покупать пошла. Видели, знаем.||А, Наташка. Да вон, погляди, объявление висит. Две недели уже никто не видел, пропала. Приходили из полиции, ходили, ходили, только ничего не нашли. Не с теми людьми связалась. В последнее время странная стала, вот и мужик ее бросил. Люди какие-то странные к ней ходили, одного я у нас в депо видела, механиком работал. Что забыл у нее, непонятно. А других не знаю. Никогда религиозной не была, а тут каждый день после работы в церковь ходила, просила о чем-то. Наверное, боялась чего-то, проблемы были. Слушай, дочка, а ты точно ей сестра? Проваливай-ка отсюда, пока я милицию не вызвала, а то я что-то много тебе рассказываю.||В винтажном, в моей молодости такого было не достать.::1, 3']

CHOOSING, TYPING_REPLY, TALKS = range(3)

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

            if storyline[:5] == u'loc::':
                lat_lon = storyline[5:].split(', ')
                lat = float(lat_lon[0])
                lon = float(lat_lon[1])
                update.message.reply_location(location=Location(lon, lat), reply_markup=markup)

            elif storyline[:5] == u'img::':
                parts = storyline[5:].split('::')
                photo = parts[0]
                caption = parts[1]
                update.message.reply_photo(photo=photo, caption=caption, reply_markup=markup)

            elif storyline[:5] == u'tlk::':
                parts = storyline[5:].split('::')
                options = parts[1].split('||')

                buttons = [str(i+1) for i in range(len(options))]
                opt_txt = u'\n'.join([b+') '+options[int(b)-1] for b in buttons])

                user_data['talks_available'] = buttons

                talks_keyboard = [buttons, [u'Закончить разговор']]
                talks_markup = ReplyKeyboardMarkup(talks_keyboard, one_time_keyboard=True, resize_keyboard=True)
                update.message.reply_text(parts[0]+'\n\n'+opt_txt, reply_markup=talks_markup)

                return TALKS
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


def regular_talk(bot, update, user_data):
    talk = update.message.text
    step = user_data['step']
    storyline = story[step]

    parts = storyline[5:].split('::')
    options = parts[1].split('||')

    responses = parts[2].split('||')
    important = parts[3].split(', ')

    if talk == u'Закончить разговор':
        if len(set(important) & set(buttons)) == 0:
            user_data['step'] = user_data.get('step', 0) + 1
            storyline = story[step]
            update.message.reply_text(
                    storyline,
                    reply_markup=markup)
            return CHOOSING
        else:
            resp = u'Кажется, я еще не спросила кое-что важное.'
    else:
        ind = int(talk)-1
        resp = u'Я: ' + options[ind] + u'\n\nДора: ' + responses[ind]
        user_data['talks_available'].remove(talk)

    buttons = user_data['talks_available']
    opt_txt = u'\n'.join([b+') '+options[int(b)-1] for b in buttons])

    talks_keyboard = [buttons, [u'Закончить разговор']]
    talks_markup = ReplyKeyboardMarkup(talks_keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    update.message.reply_text(
                    resp+'\n\n'+opt_txt,
                    reply_markup=talks_markup)

    return TALKS



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

            TALKS: [MessageHandler(Filters.text,
                                   regular_talk,
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
