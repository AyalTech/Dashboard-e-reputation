import tweepy
import twitter_api


def get_api_instance():
    auth = tweepy.OAuthHandler(twitter_api.consumer_key, twitter_api.consumer_secret)
    auth.set_access_token(twitter_api.access_key, twitter_api.access_secret)
    api = tweepy.API(auth)
    return api


def search_and_write_tweets(api, keyword, date_since, lang="en", count=2000):
    tweets = tweepy.Cursor(api.search,
                           q=keyword,
                           lang=lang,
                           since=date_since,
                           wait_on_rate_limit=True).items(count)
    tweets_arr = []
    # Iterate and print tweets
    for tweet in tweets:
        tweets_arr.append(tweet._json)

    return tweets_arr


