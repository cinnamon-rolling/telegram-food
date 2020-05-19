import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore
import utils.constants as c


# OS #
MODE = os.environ.get('MODE')


# FIREBASE #
creds = credentials.Certificate(
    'countunhealthyfoodbot.json')
firebase = firebase_admin.initialize_app(creds)
db = firestore.client()

# APP #
if MODE == "dev":
    def run(updater):
        updater.start_polling()
elif MODE == "prod":
    def run(updater):
        updater.start_webhook(listen="0.0.0.0",
                              port=c.PORT,
                              url_path=c.TOKEN)
        updater.bot.set_webhook(
            "https://{}.herokuapp.com/{}".format(c.HEROKU_APP_NAME, c.TOKEN))
        updater.idle()
else:
    print("[ERROR] No MODE specified!")
    sys.exit(1)

# APP #
# if MODE == "prod":
#     def run(updater):
#         updater.start_webhook(listen="0.0.0.0",
#                               port=c.PORT,
#                               url_path=c.TOKEN)
#         updater.bot.set_webhook(
#             "https://{}.herokuapp.com/{}".format(c.HEROKU_APP_NAME, c.TOKEN))
# else:
#     def run(updater):
#         updater.start_polling()
