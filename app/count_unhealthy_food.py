from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Dispatcher
import logging
from datetime import date
import time
import firebase_admin
from firebase_admin import credentials, firestore
import configparser
import os
import sys
from config import db, run
import utils.constants as c

logging.basicConfig(format='%(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
updater = None


updater = Updater(c.TOKEN, use_context=True)


def start_bot():
    global updater

    dispatcher = updater.dispatcher  # dispatch updates to registered handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('setnoodle', set_noodle))
    dispatcher.add_handler(CommandHandler('noodle', check_number_noodle))
    logger.info("App has started")


# /start
def start(update, context):
    number_of_noodles = 0

    username = update.message.from_user.username
    # get username
    user_id = update.message.from_user.id

    today = str(date.today())
    datetime = str(time.asctime(time.localtime(time.time())))

    welcome_text = f"Welcome {username}! I am here to check on your health! Please remember to enter your details BEFORE you consume your food to check whether you are allowed to eat!"
    update.message.reply_text(welcome_text)

    today = str(date.today())

    db = firestore.client()
    doc_ref = db.collection(u'data').document(username)

    # new users
    if db.collection(u'data').document(username).get().to_dict() is None:
        doc_ref.set({
            u'Username': str(username),
            u'ID': str(user_id),
            u'LastEnteredDate': today,
            u'TotalNoodleConsumedThisMonth': number_of_noodles
        })
    # current users
    else:
        pass

    current_month = str(date.today()).split('-')[1]

    # get month from last entry in firebase
    month = db.collection(u'data').document(
        username).get().to_dict()['LastEnteredDate'].split('-')[1]
    print('month is ', month)
    if month != current_month:
        number_of_noodles = 0
    else:
        pass

# /setnoodle


def set_noodle(update, context):
    username = update.message.from_user.username
    db = firestore.client()

    try:
        noodle_command = context.args[0].lower()
        doc_ref = db.collection(u'data').document(username)
        doc_ref.update({
            u'TotalNoodle': noodle_command
        })
        message = f'You have set {noodle_command} packet(s) of noodles per month!'
        update.message.reply_text(message)
    except:
        update.message.reply_text(
            'Please only enter - numerical (1,2,3...) commands')

# /noodle


def check_number_noodle(update, context):
    db = firestore.client()
    username = update.message.from_user.username

    today = str(date.today())
    datetime = str(time.asctime(time.localtime(time.time())))
    total_noodles = int(db.collection(u'data').document(
        username).get().to_dict()['TotalNoodle'])
    noodle_today = 0
    number_of_noodles = db.collection(u'data').document(
        username).get().to_dict()['TotalNoodleConsumedThisMonth']

    try:
        command = context.args[0].lower()

        if (command == "oops"):
            noodle_today += 1
            number_of_noodles += 1
            number_left = total_noodles - number_of_noodles
            if (number_left >= 0):
                text = f'You have eaten {number_of_noodles} packets of noodle(s), {number_left} left for the month.'
                update.message.reply_text(text)

                # get username and id
                username = update.message.from_user.username

                # update firebase
                try:
                    doc_ref = db.collection(u'data').document(username)
                    doc_ref.update({
                        u'TotalNoodleConsumedThisMonth': number_of_noodles,
                    })

                    doc_ref_date = db.collection(u'data').document(
                        username).collection(today)
                    doc_ref_date.add({
                        u'Date': datetime,
                        u'Noodle': noodle_today
                    })

                except Exception as e:
                    print(e)
            else:
                text = f'WANNA BE FAT ISIT? STOP EATING!!!'
                update.message.reply_text(text)

        elif (command == "check"):
            number_left = total_noodles - number_of_noodles
            print('number left ', number_left)
            text = f'You have eaten {number_of_noodles} packets of noodle(s), {number_left} left for the month.'
            update.message.reply_text(text)

        else:
            update.message.reply_text(
                'Please only enter - check/oops commands')
    except:
        update.message.reply_text(
            'STH WRONG Please only enter - check/oops commands')


if __name__ == "__main__":
    start_bot()
    run(updater)
