import pandas as pd
from ressources import sentiment_analysis, data_prep, statistics, co_clust, graph_analysis


class SentimentAnalysis:
    POSITIVE_PERCENTAGE = 0
    NEGATIVE_PERCENTAGE = 0
    NEUTRAL_PERCENTAGE = 0


def run():
    raw_tweets = pd.read_csv('data/extracted_tweets.csv', sep=';')
    sentiment_analysis.add_sentiment(raw_tweets)
    untrunked_tweets_df = data_prep.get_full_unique_tweets(raw_tweets)
    clean_unique_tweet_df = data_prep.get_only_unique_tweets_df(raw_tweets)
    clean_unique_tweet_df_noduplicates = data_prep.get_only_clean_text_tweets_df(raw_tweets)
    most_tweet_by_user_df = statistics.get_user_tweet_count(untrunked_tweets_df)
    most_frequent_words_df = statistics.get_top_used_words(clean_unique_tweet_df_noduplicates)
    sources_df = statistics.get_count_by_sources(untrunked_tweets_df)
    top_hashtags, top_mentions = statistics.top_used_words_and_hashtags(untrunked_tweets_df, clean_unique_tweet_df)

    SentimentAnalysis.NEGATIVE_PERCENTAGE = sentiment_analysis.get_negative_percentage(untrunked_tweets_df)
    SentimentAnalysis.POSITIVE_PERCENTAGE = sentiment_analysis.get_positive_percentage(untrunked_tweets_df)
    SentimentAnalysis.NEUTRAL_PERCENTAGE = sentiment_analysis.get_neutral_percentage(untrunked_tweets_df)

    most_tweet_by_user_df.to_csv('data/users.csv', sep=";", index=False)
    most_frequent_words_df.to_csv('data/words.csv', sep=";", index=False)
    sources_df.to_csv('data/sources.csv', sep=";", index=False)
    top_hashtags.to_csv('data/top_hashtags.csv', sep=";", index=False)
    top_mentions.to_csv('data/top_mentions.csv', sep=";", index=False)
    clean_unique_tweet_df_noduplicates.to_csv('data/clean_tweets.csv', sep=";", index=False)

    doc_matrix = co_clust.transform_doc_term_matrix(clean_unique_tweet_df_noduplicates, n_top_terms=20)

    data_c, tmp_terms, t = co_clust.run_coclust(doc_matrix)
    graph = graph_analysis.generate_graph(data_c, tmp_terms, 5, t)
    return graph
run()

