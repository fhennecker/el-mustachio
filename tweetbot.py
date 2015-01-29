import tweepy, time, sys
#from twitter import OAuth, Twitter
import os.path
import elmustachio
import re

CONSUMER_KEY = 'hXNJGzk3drcOhgonq3zsDZDSL'
CONSUMER_SECRET = 'kup9SzdPtzzghcEMq4D1kd2npmLRn3h0lNMOyn3FgTOWzjQeHv'
ACCESS_KEY = '3004088237-GzNZtNGxp2aHgIKWfdau1HZDr5QjxcIbJLUmRDv'
ACCESS_SECRET = 'ePy8t3F683CfPEmBacQEBU1JARy5oX2SaZPDACoBqMNdZ'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

elmustachio.init()

if len(sys.argv) > 1:
    url = sys.argv[1]
    id_re = re.compile(".*/status/([0-9]+)/.*")
    tweet_id = id_re.match(url).groups()[0]
    tweet = api.statuses_lookup([tweet_id])[0]
    media = tweet.entities.get("media", False)
    if media:
        media = map(lambda x:x["media_url"], media)
        status_id = tweet.id
        if hasattr(tweet, 'retweeted_status'):
            user = tweet.retweeted_status.author.screen_name
        else:
            user = tweet.author.screen_name
        downloaded_filename = str(status_id)+".jpg"
        os.system("curl "+media[0]+" -o "+downloaded_filename)
        # moustaching it
        result = elmustachio.goMoustachioGo(downloaded_filename)
        if result != None:
            # moustaching succeeded
            print result
            api.update_with_media(result, "Muchos Mustachios! @"+user,  in_reply_to_status_id=str(status_id))

else:

    while True:
        # follow every follower
        # for follower in tweepy.Cursor(api.followers).items():
        #    follower.follow()

        # pick random selfie tweet
        q = "selfie"
        tweets = api.search(q=q, count=20, filter="images")
        medias = []

        for tweet in tweets:
            media = tweet.entities.get("media", False)
            if media:
                media = map(lambda x:x["media_url"], media)
                status_id = tweet.id
                if hasattr(tweet, 'retweeted_status'):
                    user = tweet.retweeted_status.author.screen_name
                else:
                    user = tweet.author.screen_name
                safe = not tweet.possibly_sensitive
                if safe :
                    medias.append((status_id, safe, media, user))
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
                else:
                    os.system("rm "+ downloaded_filename)

        # wait for 10 minutes
        time.sleep(10*60)
