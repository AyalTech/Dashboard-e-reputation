import pandas as pd

from ressources import get_data, data_prep


def run(params):
    keywords = params['keywords']
    date_since = params['date_since']
    lang = params['lang']
    count = params['count']

    api = get_data.get_api_instance()
    raw_tweets = get_data.search_and_write_tweets(api, keywords, date_since, lang, count)

    tweet_details = data_prep.get_tweet_details(raw_tweets)

    tweets_df = pd.DataFrame(
        data=tweet_details,
        columns=['id', 'created_at', 'truncated', 'text', 'text_clean', 'screen_name', 'source',
                 'user_followers_count', 'user_friends_count', 'isRetweeted', 'retweet_count', 'user_location']
    )
    tweets_df.to_csv('data/extracted_tweets.csv', sep=";", index=False)
    return tweets_df



