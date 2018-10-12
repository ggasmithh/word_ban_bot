import telegram
from telegram.ext import MessageHandler, CommandHandler, Filters, Updater
from telegram.utils.helpers import mention_html
import calendar
import time
import logging
import atexit
import re

from config import TOKEN, BANNED_WORDS, MESSAGE

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# use our list of banned words to make a dictionary for each word and when it was last used
banned_words_dict = {word:time.time() for word in BANNED_WORDS}

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

updater.start_polling()

def word_ban(bot, update):
        
        # make a new dictionary containing any words found in both the dictionary of banned words, and in the message recieved
        found_banned_words = {word:last_usage for word, last_usage in banned_words_dict.items() if word in re.sub(r'\W+', '', update.message.text.lower())}
        
        if any(found_banned_words):
                for word in found_banned_words:

                        # figure out how long it has been since the word has been mentioned
                        current_time = time.mktime(update.message.date.timetuple())
                        delta = current_time - found_banned_words[word]

                        # update the time for the word's last usage
                        banned_words_dict[word] = current_time

                        # make a (somewhat) pretty string to tell us how long it has been
                        if delta >= 86400:
                                timestring = "{} days".format(round(delta / 86400, 2))
                                
                        elif delta >= 3600:
                                timestring = "{} hours".format(round(delta / 3600, 2))

                        elif delta >= 60:
                                timestring = "{} minutes".format(round(delta / 60, 2))
                        
                        else:
                                timestring = "{} seconds".format(round(delta))

                        # construct our reply, which consists of @'ing the user 
                        # who said the word, and the message defined in the config file
                        formatted_message = "@" + update.message.from_user.username + MESSAGE.format(timestring)

                        #send it
                        update.message.reply_text(formatted_message)

word_ban_handler = MessageHandler(Filters.text, word_ban)
dispatcher.add_handler(word_ban_handler)

# make sure that the user cannot exit the program without the bot 
# shutting down gracefully
def exit_handler():
        updater.stop()
        updater.is_idle = False

atexit.register(exit_handler)

updater.idle()
