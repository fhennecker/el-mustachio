import tweepy, time, sys
#from twitter import OAuth, Twitter
import os.path

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

while True:
    # follow every follower
    for follower in tweepy.Cursor(api.followers).items():
        follower.follow()

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
            downloaded_filename = "hello.jpg"
            os.system("curl "+media[2][0]+" > "+downloaded_filename)
            # moustaching it
            os.system("python elmustachios-cli.py "+ downloaded_filename)
            if os.path.isfile("elmustachios-"+downloaded_filename):
                print "Moustaching succeeded"
                moustached = True
                #api.update_with_media("elmustachios-"+downloaded_filename, "", media[0])
                os.system("rm "+ downloaded_filename)
                #os.system("rm "+ "elmustachios-"+downloaded_filename)
                os.system("rm "+ "debug-"+downloaded_filename)
            else:
                os.system("rm "+ downloaded_filename)

    # wait for 10 minutes
    time.sleep(10*60)
