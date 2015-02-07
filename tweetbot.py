import tweepy
import time
import sys
import os.path
import subprocess
import elmustachio
import re
import sqlite3
from configobj import ConfigObj

# Load configuration
config = ConfigObj('config')
DB_NAME = config['DB_NAME']
CONSUMER_KEY = config['CONSUMER_KEY']
CONSUMER_SECRET = config['CONSUMER_SECRET']
ACCESS_KEY = config['ACCESS_KEY']
ACCESS_SECRET = config['ACCESS_SECRET']
INTERVAL = int(config['INTERVAL'])
NSFW_WORDS = config['NSFW_WORDS']
USER_BLACKLIST = config['USER_BLACKLIST']

def nsfw_filter(s):
    for w in NSFW_WORDS:
        if w in s:
            return True
    return False


# Twitter authentication
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# Opening blacklist DB (used to avoid reposting images)
blacklist_db = sqlite3.connect(DB_NAME)
blacklist_cursor = blacklist_db.cursor()
# Testing if the table already exist, if not creates it
blacklist_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='blacklist';")
if blacklist_cursor.fetchone() == None:
    blacklist_cursor.execute("CREATE TABLE blacklist (id UNISGNED BIG INT PRIMARY KEY ASC);")

# Initialising El Mustachio algorithm
elmustachio.init()

# If an argument was given -> one shot mode
if len(sys.argv) > 1:
    # Extracting the id from an url given as an argument
    url = sys.argv[1]
    id_re = re.compile(".*/status/([0-9]+).*")
    tweet_id = id_re.match(url).groups()[0]
    # Looking up the tweet using the api and retrieving the media
    tweet = api.statuses_lookup([tweet_id])[0]
    media = tweet.entities.get("media", False)
    if media:
        media = map(lambda x:x["media_url"], media)
        # If it's a retweet get the info from the original tweet
        if hasattr(tweet, 'retweeted_status'):
            user = tweet.retweeted_status.author.screen_name
            status_id = tweet.retweeted_status.id
        else:
            user = tweet.author.screen_name
            status_id = tweet.id
        # Download the image
        downloaded_filename = str(status_id)+".jpg"
        subprocess.call(["curl", media[0], "-o", downloaded_filename])
        # Mustaching it
        result = elmustachio.goMustachioGo(downloaded_filename)
        if result != None:
            # Mustaching succeeded
            print result
            # Tweet the result
            api.update_with_media(result, "Muchos Mustachios! @"+user,  in_reply_to_status_id=str(status_id))
        else:
            print('El Mustachio failed :(')
    else:
        print('No picture found.')

# Else it's the bot mode
else:
    while True:
        # Some attempt at sanity in the search for selfies
        q = "selfie -justin -bieber -1d -\"one direction\" -boobs -sex -nsfw -pussy -porn -sexy -fap -cock -dick -nude -fuck"
        tweets = api.search(q=q, count=20, result_type="recent", filter="images")

        medias = []
        for tweet in tweets:
            media = tweet.entities.get("media", False)
            if media:
                media = map(lambda x:x["media_url"], media)
                # If it's a retweet get the info from the original tweet
                if hasattr(tweet, 'retweeted_status'):
                    user = tweet.retweeted_status.author.screen_name
                    status_id = tweet.retweeted_status.id
                else:
                    user = tweet.author.screen_name
                    status_id = tweet.id
                # Checking for potential NSFW indicators
                nsfw = tweet.possibly_sensitive or nsfw_filter(user.lower()) or nsfw_filter(tweet.text.lower())
                # Checking if it was already processed
                blacklist_cursor.execute("SELECT id FROM blacklist WHERE id=?;", (status_id,))
                # If everything is fine, add it to the media list
                if not nsfw and user not in USER_BLACKLIST and blacklist_cursor.fetchone() == None:
                    medias.append((status_id, media, user))
        print medias
        mustached = False
        for media in medias:
            # Try all the media until we succeed
            if not mustached:
                # Downloading media
                downloaded_filename = 'img/'+str(media[0])+".jpg"
                subprocess.call(["curl", media[1][0], "-o", downloaded_filename])
                # Mustaching it
                result = elmustachio.goMustachioGo(downloaded_filename)
                if result != None:
                    # Mustaching succeeded
                    print result
                    # Tweet the result
                    api.update_with_media(result, "Muchos Mustachios! @"+media[2],  in_reply_to_status_id=str(media[0]))
                    # Add it to the db
                    blacklist_cursor.execute("INSERT INTO blacklist VALUES (?);", (media[0],))
                    blacklist_db.commit()
                    mustached = True
                else:
                    subprocess.call(["rm", downloaded_filename])

        # wait for INTERVAL
        time.sleep(INTERVAL)
