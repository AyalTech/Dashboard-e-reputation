from textblob import TextBlob


def add_sentiment(tweets_df):
    tweets_df['Subjectivity'] = tweets_df['text'].apply(getSubjectivity)
    tweets_df['Polarity'] = tweets_df['text'].apply(getPolarity)
    tweets_df['Sentiment'] = tweets_df['text'].apply(getSentiment)


# Create a function to get the subjectivity
def getSubjectivity(text):
    return TextBlob(text).sentiment.subjectivity


# Create a function to get the polarity
def getPolarity(text):
    return TextBlob(text).sentiment.polarity


# Create a function to get the sentiment
def getSentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment[0] > 0:
        return 'Positive'
    elif analysis.sentiment[0] < 0:
        return 'Negative'
    else:
        return 'Neutre'


def get_positive_percentage(tweets_df_no_trunced):
    ptweets = tweets_df_no_trunced[tweets_df_no_trunced.Sentiment == 'Positive']
    ptweets = ptweets['text']
    if tweets_df_no_trunced.shape[0] != 0:
        return round((ptweets.shape[0] / tweets_df_no_trunced.shape[0]) * 100, 1)
    return 0


def get_negative_percentage(tweets_df_no_trunced):
    ntweets = tweets_df_no_trunced[tweets_df_no_trunced.Sentiment == 'Negative']
    ntweets = ntweets['text']
    if tweets_df_no_trunced.shape[0] != 0:
        return round((ntweets.shape[0] / tweets_df_no_trunced.shape[0]) * 100, 1)
    return 0


def get_neutral_percentage(tweets_df_no_trunced):
    ntweets = tweets_df_no_trunced[tweets_df_no_trunced.Sentiment == 'Neutre']
    ntweets = ntweets['text']
    if tweets_df_no_trunced.shape[0] !=0:
        return round((ntweets.shape[0] / tweets_df_no_trunced.shape[0]) * 100, 1)
    return 0