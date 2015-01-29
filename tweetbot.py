import tweepy, time, sys
 
CONSUMER_KEY = 'hXNJGzk3drcOhgonq3zsDZDSL'
CONSUMER_SECRET = 'kup9SzdPtzzghcEMq4D1kd2npmLRn3h0lNMOyn3FgTOWzjQeHv'
ACCESS_KEY = '3004088237-GzNZtNGxp2aHgIKWfdau1HZDr5QjxcIbJLUmRDv'
ACCESS_SECRET = 'ePy8t3F683CfPEmBacQEBU1JARy5oX2SaZPDACoBqMNdZ'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
 
#api.update_status(status='The world needs more moustaches')


while True:
	# follow every follower
	for follower in tweepy.Cursor(api.followers).items():
	    follower.follow()

	# pick random selfie tweet

	# moustache said selfie

	# post moustached selfie
	#api.update_status(status='The world needs more moustaches')

	# wait for 10 minutes
	time.sleep(10*60)