import re
import string

import pandas as pd
import preprocessor as p
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

from ressources.text_paterns import TextPatterns


def clean_tweets(tweet):
    emoticons = TextPatterns.EMOTICONS_HAPPY.union(TextPatterns.EMOTICONS_SAD)
    stop_words = set(stopwords.words('english'))
    collection_words = ['rt', 'n', '\'s', '``', '\'\'', 'n\'t', 'u', 'gt', 'na', 'AT_USER', 'amp',
                        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaawwwwwwwwwwwwwwwwwwlllll']

    # after tweepy preprocessing the colon symbol left remain after      #removing mentions
    tweet = re.sub(r':', '', tweet)
    tweet = re.sub(r'‚Ä¶', '', tweet)

    # replace consecutive non-ASCII characters with a space
    tweet = re.sub(r'[^\x00-\x7F]+', ' ', tweet)

    # remove emojis from tweet
    tweet = TextPatterns.EMOJI_PATTERN.sub(r'', tweet)
    # Others clean
    tweet = tweet.lower()  # convert text to lower-case
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)  # remove URLs
    tweet = re.sub(r"http\S+", "", tweet)  # remove URLs
    tweet = re.sub('@[^\s]+', 'AT_USER', tweet)  # remove usernames
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)  # remove the # in #hashtag
    tweet = tweet.replace('.', '')  # remove ...
    tweet = word_tokenize(tweet)  # remove repeated characters (helloooooooo into hello)
    filtered_tweet = []
    ps = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    # looping through conditions
    for w in tweet:
        # check tokens against stop words , emoticons and punctuations
        if w not in stop_words and w not in emoticons and w not in string.punctuation and w not in collection_words:
            w_lematize = lemmatizer.lemmatize(w)
            w_lematize_stem = ps.stem(w_lematize)
            if w.find('s') == 2 and len(w) == 3:
                w_lematize_stem = w
            if is_not_number(w_lematize_stem):
                filtered_tweet.append(w_lematize_stem)
    return ' '.join(filtered_tweet)


def is_not_number(s):
    if s.find('s') == -1 or len(s) != 3:
        for c in s:
            try:
                float(c)
                return False
            except ValueError:
                pass

            try:
                import unicodedata
                unicodedata.numeric(s)
                return False
            except (TypeError, ValueError):
                pass
    return True


def getSource(source):
    pos1 = source.find("Twitter")
    pos2 = source.find("</a>")
    str_source = source[(pos1 + 12):pos2]
    if str_source != "Android" and str_source not in "Web" and str_source != "iPhone" and str_source != "iPad":
        return "Web App"
    else:
        return str_source


def is_retweeted(retweeted_status):
    if retweeted_status:
        return True
    else:
        return False


def get_tweet_details(tweets_array):
    for tweets in tweets_array:
        if 'retweeted_status' not in tweets:
            tweets['retweeted_status'] = None

    return [
        [tweet['id'], tweet['created_at'], tweet['truncated'], tweet['text'], clean_tweets(p.clean(tweet['text'])),
         tweet['user']['screen_name'], getSource(tweet['source']),
         tweet['user']['followers_count'], tweet['user']['friends_count'], is_retweeted(tweet['retweeted_status']),
         tweet['retweet_count'], tweet['user']['location']] for tweet in tweets_array]


def get_full_unique_tweets(tweets_df):
    tweets_df_no_trunced = tweets_df[tweets_df['truncated'] == False]
    tweets_df_no_trunced_no_duplicate = tweets_df_no_trunced.copy().drop_duplicates(subset='text')
    return tweets_df_no_trunced_no_duplicate[
        tweets_df_no_trunced_no_duplicate['text_clean'] != '']


def get_only_unique_tweets_df(tweets_df_no_trunced_no_duplicate):
    df_unique_text = pd.DataFrame(tweets_df_no_trunced_no_duplicate, columns=['id', 'text'])
    df_unique_text.columns = ['id_tweet', 'text']
    df_unique_text.index.name = 'id'
    return df_unique_text


def get_only_clean_text_tweets_df(tweets_df_no_trunced_no_duplicate):
    df_unique_text_clean = pd.DataFrame(tweets_df_no_trunced_no_duplicate, columns=['id', 'text_clean'])
    df_unique_text_clean.columns = ['id_tweet', 'text_clean']
    df_unique_text_clean.index.name = 'id'
    return df_unique_text_clean
