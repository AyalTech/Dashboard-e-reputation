import collections
import itertools
import string

import pandas as pd


def get_total_untruncated_tweets(tweets_df_no_trunced):
    return len(tweets_df_no_trunced.index)


def get_total_unique_users(tweets_df_no_trunced):
    return len(tweets_df_no_trunced['screen_name'].unique())


def get_total_original_tweets(tweets_df_no_trunced):
    return len(tweets_df_no_trunced[tweets_df_no_trunced['isRetweeted'] is False])


def get_total_duplicates(tweets_df_no_trunced, tweets_df_no_trunced_no_duplicate):
    return len(tweets_df_no_trunced) - len(tweets_df_no_trunced_no_duplicate)


def get_most_retweeted(tweets_df_no_trunced):
    tweets_df_no_trunced = tweets_df_no_trunced.sort_values(by='isRetweeted', ascending=False)
    return tweets_df_no_trunced.reset_index(drop=True)


def get_user_tweet_count(tweets_df_no_trunced_no_duplicate):
    all_screen_name = list(itertools.chain(tweets_df_no_trunced_no_duplicate['screen_name']))
    counts_screen_name = collections.Counter(all_screen_name)
    counts_screen_name.most_common(15)
    return pd.DataFrame(counts_screen_name.most_common(15),
                        columns=['screen_name', 'count'])


def get_count_by_sources(tweets_df_no_trunced_no_duplicate):
    all_source = list(itertools.chain(tweets_df_no_trunced_no_duplicate['source']))
    counts_source = collections.Counter(all_source)
    df_source = pd.DataFrame(counts_source.most_common(15),
                             columns=['source', 'count'])
    df_source.loc[4, 'source'] = 'Non reconnu'
    return df_source


def top_used_words_and_hashtags(df_unique_text, tweets_df_no_trunced_no_duplicate):
    tag_dict = {}
    mention_dict = {}

    for i in df_unique_text.index:
        tweet_text = tweets_df_no_trunced_no_duplicate['text'][i]
        tweet = tweet_text.lower()
        tweet_tokenized = tweet.split()

        for word in tweet_tokenized:
            # Hashtags - tokenize and build dict of tag counts
            if word[0:1] == '#' and len(word) > 1:
                key = word.translate(str.maketrans("", "", string.punctuation))
                if key in tag_dict:
                    tag_dict[key] += 1
                else:
                    tag_dict[key] = 1

            # Mentions - tokenize and build dict of mention counts
            if word[0:1] == '@' and len(word) > 1:
                key = word.translate(str.maketrans("", "", string.punctuation))
                if key in mention_dict:
                    mention_dict[key] += 1
                else:
                    mention_dict[key] = 1

    hashtags_df = pd.DataFrame.from_dict(tag_dict, orient='index', columns=['occurence']).reset_index().\
        rename(columns={'index': 'hashtag'})
    mention_df = pd.DataFrame.from_dict(mention_dict, orient='index', columns=['occurence']).reset_index().\
        rename(columns={'index': 'mention'})
    return hashtags_df, mention_df


def get_top_used_words(df_unique_text_clean):
    text_tweet = df_unique_text_clean['text_clean'].astype(str)
    words_in_tweet = [tweet.lower().split() for tweet in text_tweet]
    # List of all words across tweets
    all_words = list(itertools.chain(*words_in_tweet))

    # Count each word across all tweets - notice there are still stop words
    counts = collections.Counter(all_words)
    return pd.DataFrame(counts.most_common(40),
                        columns=['words', 'count'])
