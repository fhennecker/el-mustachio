import tweepy, time, sys
#from twitter import OAuth, Twitter
import os.path
import elmustachio
import re
import sqlite3

def nsfw_filter(s):
    nsfw_words = ["justin", "bieber", "1d", "one direction", "5/5", "niall", "zain", "zayn", "nsfw", "porn", "nude", "sex", "boob", "pussy", "pussies", "dick", "cock", "bitch", "fuck", "sexy", "milf", "tits", "ass "]
    for w in nsfw_words:
        if w in s:
            return True
    return False

CONSUMER_KEY = 'hXNJGzk3drcOhgonq3zsDZDSL'
CONSUMER_SECRET = 'kup9SzdPtzzghcEMq4D1kd2npmLRn3h0lNMOyn3FgTOWzjQeHv'
ACCESS_KEY = '3004088237-GzNZtNGxp2aHgIKWfdau1HZDr5QjxcIbJLUmRDv'
ACCESS_SECRET = 'ePy8t3F683CfPEmBacQEBU1JARy5oX2SaZPDACoBqMNdZ'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

blacklist_db = sqlite3.connect('blacklist.db')
blacklist_cursor = blacklist_db.cursor()
blacklist_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='blacklist';")
if blacklist_cursor.fetchone() == None:
    blacklist_cursor.execute("CREATE TABLE blacklist (id UNISGNED BIG INT PRIMARY KEY ASC);")

user_blacklist = ["SteveK_UK", "PantyhoseMilfs", "Bitch2Cuck", "FuckWatchyou", "Selfies_Galore", "Selfie_it", "selfie0queen", "EsVirall", "sexy_selfie_xxx", "HottestExies"]

elmustachio.init()

if len(sys.argv) > 1:
    url = sys.argv[1]
    id_re = re.compile(".*/status/([0-9]+).*")
    tweet_id = id_re.match(url).groups()[0]
    tweet = api.statuses_lookup([tweet_id])[0]
    media = tweet.entities.get("media", False)
    if media:
        media = map(lambda x:x["media_url"], media)
        if hasattr(tweet, 'retweeted_status'):
            user = tweet.retweeted_status.author.screen_name
            status_id = tweet.retweeted_status.id
        else:
            user = tweet.author.screen_name
            status_id = tweet.id
        downloaded_filename = str(status_id)+".jpg"
        os.system("curl "+media[0]+" -o "+downloaded_filename)
        # moustaching it
        result = elmustachio.goMoustachioGo(downloaded_filename)
        if result != None:
            # moustaching succeeded
            print result
            api.update_with_media(result, "Muchos Mustachios! @"+user,  in_reply_to_status_id=str(status_id))
        else:
            print('El Moustachio failed :(')
    else:
        print('No picture found.')

else:

    while True:
        # follow every follower
        # for follower in tweepy.Cursor(api.followers).items():
        #    follower.follow()

        # pick random selfie tweet
        q = "selfie -justin -bieber -ellen -kanye -boobs -sex -nsfw -pussy -porn -sexy -fap -cock -dick -nude -fuck"
        tweets = api.search(q=q, count=20, result_type="recent", filter="images")
        medias = []

        for tweet in tweets:
            media = tweet.entities.get("media", False)
            if media:
                media = map(lambda x:x["media_url"], media)
                if hasattr(tweet, 'retweeted_status'):
                    user = tweet.retweeted_status.author.screen_name
                    status_id = tweet.retweeted_status.id
                else:
                    user = tweet.author.screen_name
                    status_id = tweet.id
                nsfw = tweet.possibly_sensitive or nsfw_filter(user.lower()) or nsfw_filter(tweet.text.lower())
                blacklist_cursor.execute("SELECT id FROM blacklist WHERE id=?;", (status_id,))
                if not nsfw and user not in user_blacklist and blacklist_cursor.fetchone() == None:
                    medias.append((status_id, nsfw, media, user))
        print medias
        moustached = False
        for media in medias:
            if not moustached:
                # downloading media
                downloaded_filename = 'img/'+str(media[0])+".jpg"
                os.system("curl "+media[2][0]+" -o "+downloaded_filename)
                # moustaching it
                result = elmustachio.goMoustachioGo(downloaded_filename)
                if result != None:
                    # moustaching succeeded
                    print result
                    api.update_with_media(result, "Muchos Mustachios! @"+media[3],  in_reply_to_status_id=str(media[0]))
                    moustached = True
                    blacklist_cursor.execute("INSERT INTO blacklist VALUES (?);", (media[0],))
                    blacklist_db.commit()
                else:
                    os.system("rm "+ downloaded_filename)

        # wait for 10 minutes
        time.sleep(10*60)
