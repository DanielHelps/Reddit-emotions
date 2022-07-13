import re
import datetime



def is_wanted(word_tag_tuple: tuple) -> bool:
    """A function that checks if word is one of the tagged words (doesn't really contribute to the decision if its a positive or negative),
    and doesn't include it in the training if it is

    Args:
        word_tag_tuple (tuple): word with its tagging 
        (default tagging list can be found here: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html)

    Returns:
        bool: returns True if the word is wanted and False if it isn't
    """    
    # 
    global unwanted
    word, tag = word_tag_tuple
    if not word.isalpha() or word in unwanted:
        return False
    if tag == "PRP$" or tag == "IN" or tag == "PRP" or tag == "MD" or tag == "TO" or len(tag) == 1:
        return False
    return True



# def is_correct(tweet: str, positive_check: bool, positive_tweets: list) -> bool:
#     global counter
#     if tweet in positive_tweets:
#         if positive_check:
#             counter += 1
#             return True
#         else:
#             return False
#     elif not positive_check:
#         counter += 1
#         return True
#     return False


def find_expressions(tweet: str, sad_expression: list, happy_expression: list) -> int:
    """finds expressions (emojis) in the text 

    Args:
        tweet (str): a tweet to check
        sad_expression (list): list of sad expressions to check
        happy_expression (list): list of happy expressions to check

    Returns:
        int: the "emoji" score of the tweet (for every happy emoji, get +1, for every sad emoji,
        get -1, the total sum is returned)
    """    
    exp_count = 0
    for emote in sad_expression:
        if emote in tweet:
            exp_count -= 1
    for emote in happy_expression:
        if emote in tweet:
            exp_count += 1
    return exp_count


def remove_tweet_unwanted(tweet: str) -> str:
    """removes unwanted characters from tweets (@ at someone, links etc..)

    Args:
        tweet (str): the tweet to check

    Returns:
        str: the upated tweet without all the garbage unrequried text
    """    
    updated_tweet = re.sub("@\w+", "", tweet)
    updated_tweet = re.sub("http\S+", "", updated_tweet)
    updated_tweet = re.sub(" .{1} ", " ", updated_tweet)
    return updated_tweet


def extract_features(text: str, top_100_positive: list, top_100_negative: list, sia) -> dict:
    """Extracts the features of the text (compound score, emoji score, and positive wordcout) so it can be 
    classified by the trained classifier

    Args:
        text (str): the text that is being checked
        top_100_positive (list): list of top 100 positive words used in the training corpus
        top_100_negative (list): list of top 100 negative words used in the training corpus
        sia (SentimentIntensityAnalyzer): VADER instance to extract initial compound score

    Returns:
        dict: the dictionary of extracted features for the text
    """    
    import nltk
    from statistics import mean

    features = dict()
    pos_wordcount = 0
    compound_scores = list()
    positive_scores = list()
    exp_count = 0
    sad_expressions = [":(", ":'(", ":-(", ":'-(", "=("]
    happy_expressions = [":)", ":-)", ":D", "=)", ":]", ":>", ":^)"]

    # Tokenize text
    for sentence in nltk.sent_tokenize(text):
        # Get the emoji score
        exp_count += find_expressions(sentence, sad_expressions, happy_expressions)
        # Get the positive wordcount feature
        for word in nltk.word_tokenize(sentence):
            if word.lower() in top_100_positive:
                pos_wordcount += 1
            elif word.lower() in top_100_negative:
                pos_wordcount -= 1
        # Get the compound score using VADER
        compound_scores.append(sia.polarity_scores(sentence)["compound"])
        positive_scores.append(sia.polarity_scores(sentence)["pos"])

    
    features["mean_compound"] = mean(compound_scores)
    features["mean_positive"] = mean(positive_scores)
    features["pos_wordcount"] = pos_wordcount
    # Currently not using emoji score as it doesn't give information for majority of texts

    return features

    
def main_training(extra_positive_data=[], extra_negative_data=[]) -> tuple:
    """Trains the classifier with the extra positive and negative data from the
    training section and creates a new updated classifier to use for search

    Args:
        extra_positive_data (list, optional): new positive data to train the classifier with. Defaults to [].
        extra_negative_data (list, optional): new negative data to train the classifier with. Defaults to [].

    Returns:
        tuple: name of new classifier and the date it was classified
    """    
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.corpus import twitter_samples
    from random import shuffle
    import re
    from statistics import mean
    from .models import Classifier
    
    
    sia = SentimentIntensityAnalyzer()

    
    global counter
    counter = 0

    # create list of common unwanted words
    twitter_samples.fileids()
    global unwanted
    unwanted = nltk.corpus.stopwords.words("english")
    unwanted.extend([w.lower() for w in nltk.corpus.names.words()])


    neg_tweets = twitter_samples.strings('negative_tweets.json')
    # Add the new negative sentences from users training
    neg_tweets += extra_negative_data


    pos_tweets = twitter_samples.strings('positive_tweets.json')
    # Add the new positive sentences from users training
    pos_tweets += extra_positive_data
    all_tweets = neg_tweets + pos_tweets
    neg_tweet_words = []
    pos_tweet_words = []
    # Create a list with the most informative negative tweet words for each sentence, then do
    # the same with positive words
    for i, tweet in enumerate(neg_tweets):
        tweet = remove_tweet_unwanted(tweet)
        tweet_words_tags = nltk.pos_tag(nltk.word_tokenize(tweet))
        neg_tweet_words += [word for word, tag in filter(is_wanted, tweet_words_tags)]
        pass

    for i, tweet in enumerate(pos_tweets):
        tweet = remove_tweet_unwanted(tweet)
        tweet_words_tags = nltk.pos_tag(nltk.word_tokenize(tweet))
        pos_tweet_words += [word for word, tag in filter(is_wanted, tweet_words_tags)]
        pass

    # Get most frequent words in positive / negative tweets 
    positive_fd = nltk.FreqDist(pos_tweet_words)
    negative_fd = nltk.FreqDist(neg_tweet_words)

    common_set = set(positive_fd).intersection(negative_fd)

    # Delete common words that appear both in positive and negative words list
    for word in common_set:
        del positive_fd[word]
        del negative_fd[word]

    top_100_positive = {word for word, count in positive_fd.most_common(100)}
    top_100_negative = {word for word, count in negative_fd.most_common(100)}

    shuffle(all_tweets)


    features = [
        (extract_features(tweet,top_100_positive,top_100_negative, sia),"pos")
        for tweet in pos_tweets
    ]
    features.extend([
        (extract_features(tweet,top_100_positive,top_100_negative, sia),"neg")
        for tweet in neg_tweets
    ])
    pass
    # Supervised vs unsupervised training data ratio
    supervised_ratio = (5/6)
    train_count = int(len(features) * supervised_ratio)
    shuffle(features)
    # Train classifier with the supervised information
    classifier = nltk.NaiveBayesClassifier.train(features[:train_count])
    classifier.show_most_informative_features(10)
    print(nltk.classify.accuracy(classifier, features[train_count:]))
    date = datetime.datetime.date(datetime.datetime.now())
    # Push the new classifier into the database
    classifier_name = f'classifier_{date}.pickle'
    a = Classifier(classifier_obj=classifier, classifier_date=date)
    a.save()

    return classifier_name, date
    