import tweepy, time, sys
from twitter import OAuth, Twitter
import os.path

CONSUMER_KEY = 'hXNJGzk3drcOhgonq3zsDZDSL'
CONSUMER_SECRET = 'kup9SzdPtzzghcEMq4D1kd2npmLRn3h0lNMOyn3FgTOWzjQeHv'
ACCESS_KEY = '3004088237-GzNZtNGxp2aHgIKWfdau1HZDr5QjxcIbJLUmRDv'
ACCESS_SECRET = 'ePy8t3F683CfPEmBacQEBU1JARy5oX2SaZPDACoBqMNdZ'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

autht = OAuth(ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
t = Twitter(auth=autht)
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
	tweets = t.search.tweets(q=q, filter="images")
	medias = []

	for tweet in tweets["statuses"]:
		media = tweet["entities"].get("media", False)
		if media:
			media = map(lambda x:x["media_url"], media)
			status_id = tweet["id"]
			if not str(media) in open(mediasfile).read():
				medias.append((status_id, media))
				with open(mediasfile, "a") as f:
					f.write(str(media))
					f.write("\n")

    counter = 0
    moustached = False
	for media in medias:
        if not moustached:
            # downloading media
            downloaded_filename = str(counter)+".jpg"
            os.system("curl "+media[1]+" > "+downloaded_filename)
            # moustaching it
    		os.system("python elmustachios-cli.py "+ downloaded_filename)
            if os.path.isfile("elmustachios-"+downloaded_filename):
                # moustaching succeeded
                #api.update_with_media("elmustachios-"+downloaded_filename, "", media[0])
            else:
                os.system("rm "+ downloaded_filename)

	# wait for 10 minutes
	time.sleep(10*60)
