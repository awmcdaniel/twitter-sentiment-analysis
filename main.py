import fix_path
import httplib2
import webapp2
import twitter_authentication
import tweepy
from oauth2client.appengine import AppAssertionCredentials
from apiclient.discovery import build

class twoot(webapp2.RequestHandler):
	def get(self):
		# authenticate to the Twitter API via tweepy
		auth = tweepy.OAuthHandler(twitter_authentication.consumer_key, twitter_authentication.consumer_secret)
		auth.set_access_token(twitter_authentication.access_token, twitter_authentication.access_token_secret)

		api = tweepy.API(auth)

		# authenticate to the Google Prediction API
		http = AppAssertionCredentials('https://www.googleapis.com/auth/prediction').authorize(httplib2.Http())
		service = build('prediction', 'v1.6', http=http)

		# call for the 10 most recent tweets matching query "Donald Trump"
		search_results = api.search(q="Donald Trump", lang="en", count=10)

		# iterate through our tweets
		for original_tweet in search_results:
			# sanitize each tweet for the Prediction API
			sanitized_tweet = "".join(char for char in original_tweet.text if char not in ('!', '?', '.', ',', ':', ';', '"', '(', ')', '[', ']', '{', '}', '*'))
			sanitized_tweet = sanitized_tweet.lower()

			# pass the sanizited tweet to the Prediction API
			result = service.trainedmodels().predict(project='sentiment-analysis-2016', id='tweetsentiments', body={'input': {'csvInstance': [sanitized_tweet]}}).execute()
			
			# print each tweet, along with the Prediction API's evaluation
			self.response.write(result['outputLabel'] + ": " + sanitized_tweet + '<br>')

app = webapp2.WSGIApplication([
	('/', twoot),
], debug = True)