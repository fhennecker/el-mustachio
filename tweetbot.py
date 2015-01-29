import tweepy, time, sys
#from twitter import OAuth, Twitter
import os.path
import elmustachio

CONSUMER_KEY = 'hXNJGzk3drcOhgonq3zsDZDSL'
CONSUMER_SECRET = 'kup9SzdPtzzghcEMq4D1kd2npmLRn3h0lNMOyn3FgTOWzjQeHv'
ACCESS_KEY = '3004088237-GzNZtNGxp2aHgIKWfdau1HZDr5QjxcIbJLUmRDv'
ACCESS_SECRET = 'ePy8t3F683CfPEmBacQEBU1JARy5oX2SaZPDACoBqMNdZ'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

mediasfile = "medias.txt"
if not os.path.isfile(mediasfile):
    f = open(mediasfile, "w")
    f.close()

elmustachio.init()

while True:
    # follow every follower
    # for follower in tweepy.Cursor(api.followers).items():
    #    follower.follow()

    # pick random selfie tweet
    q = "selfie"
    tweets = api.search(q=q, count=10, filter="images")
    medias = []

    for tweet in tweets:
        media = tweet.entities.get("media", False)
        if media:
            media = map(lambda x:x["media_url"], media)
            status_id = tweet.id
            safe = not tweet.possibly_sensitive
            if safe and not str(media) in open(mediasfile).read():
                medias.append((status_id, safe, media))
                with open(mediasfile, "a") as f:
                    f.write(str(media))
                    f.write("\n")
    print medias
    moustached = False
    for media in medias:
        if not moustached:
            # downloading media
            downloaded_filename = str(media[0])+".jpg"
            os.system("curl "+media[2][0]+" -o "+downloaded_filename)
            # moustaching it
            result = elmustachio.goMoustachioGo(downloaded_filename)
            if result != None:
                # moustaching succeeded
                print result
                api.update_with_media(result, "", media[0])
                moustached = True
            else:
                os.system("rm "+ downloaded_filename)

    # wait for 10 minutes
    time.sleep(10*60)
