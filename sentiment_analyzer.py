from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import numpy as np
import pandas as pd

import credentials


class TwitterClient():

    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(
            self.twitter_client.user_timeline, id=self.twitter_user
        ).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets

    def get_tweets_by_search(self, num_tweets, keyword="", date_since="2021-01-01"):
        # https://www.earthdatascience.org/courses/use-data-open-source-python/intro-to-apis/twitter-data-in-python/
        tweets = []
        for tweet in Cursor(
            self.twitter_client.search, 
            q=keyword,
            lang="en",
            since=date_since
        ).items(num_tweets):
            tweets.append(tweet)

        return tweets



class TwitterAuthenticator():
    """
    Class for authenticating the twitter app
    """
    def authenticate_twitter_app(self):
         # handles twitter authentication and the connection to the twitter Streaming API
        auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
        auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
        return auth
 

class TwitterStreamer():
    """
    Class for streaming and processing live tweets
    """

    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        stream.filter(track=hash_tag_list)


class TwitterListener(StreamListener):
    """
    Base listener class that prints streamed tweets to stdout
    """

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            # Return false on_data method in case rate limit occurs
            return False
        print(status)



class TweetAnalyzer():
    """
    Class for analyzing content from tweets
    """
    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        return df


if __name__ == '__main__':
    # hash_tag_list = ['donald trump', 'hilary clinton', 'barack obama', 'berny sanders']
    # fetched_tweets_filename = "tweets.json"

    # twitter_client = TwitterClient('pycon')
    # print(twitter_client.get_user_timeline_tweets(1))
    # # twitter_streamer = TwitterStreamer()
    # # twitter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    # api = twitter_client.get_twitter_client_api()
    # tweets = api.user_timeline(screen_name="pycon", count=20) # apprently, Donald trump is suspended
    # print(tweets)

    # for checking the properties/keys of the tweet object
    # print(dir(tweets[0]))

    # df = tweet_analyzer.tweets_to_data_frame(tweets)
    # print(df.head(5))

    tweets = twitter_client.get_tweets_by_search(20, "vaccination philippines", "2021-02-01")
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    print(df.head(5))