import re
import datetime



def is_wanted(word_tag_tuple: tuple) -> bool:
    global unwanted
    word, tag = word_tag_tuple
    if not word.isalpha() or word in unwanted:
        return False
    if tag == "PRP$" or tag == "IN" or tag == "PRP" or tag == "MD" or tag == "TO" or len(tag) == 1:
        return False
    return True


def check_positive(tweet: str, sia) -> bool:
    score = sia.polarity_scores(tweet)["compound"]
    if score > 0: return True
    return False


def is_correct(tweet: str, positive_check: bool, positive_tweets: list) -> bool:
    global counter
    if tweet in positive_tweets:
        if positive_check:
            counter += 1
            return True
        else:
            return False
    elif not positive_check:
        counter += 1
        return True
    return False


def find_expressions(tweet: str, sad_expression: list, happy_expression: list):
    exp_count = 0
    for emote in sad_expression:
        if emote in tweet:
            exp_count -= 1
    for emote in happy_expression:
        if emote in tweet:
            exp_count += 1
    return exp_count


def remove_tweet_unwanted(tweet: str) -> str:
    updated_tweet = re.sub("@\w+", "", tweet)
    updated_tweet = re.sub("http\S+", "", updated_tweet)
    updated_tweet = re.sub(" .{1} ", " ", updated_tweet)
    return updated_tweet


def extract_features(text, top_100_positive, top_100_negative, sia):
    import nltk
    from statistics import mean

    features = dict()
    pos_wordcount = 0
    compound_scores = list()
    positive_scores = list()
    exp_count = 0
    sad_expressions = [":(", ":'(", ":-(", ":'-(", "=("]
    happy_expressions = [":)", ":-)", ":D", "=)", ":]", ":>", ":^)"]

    for sentence in nltk.sent_tokenize(text):
        exp_count += find_expressions(sentence, sad_expressions, happy_expressions)
        for word in nltk.word_tokenize(sentence):
            if word.lower() in top_100_positive:
                pos_wordcount += 1
            elif word.lower() in top_100_negative:
                pos_wordcount -= 1
        compound_scores.append(sia.polarity_scores(sentence)["compound"])
        positive_scores.append(sia.polarity_scores(sentence)["pos"])

    # Adding 1 to the final compound score to always have positive numbers
    # since some classifiers you'll use later don't work with negative numbers.
    features["mean_compound"] = mean(compound_scores)
    features["mean_positive"] = mean(positive_scores)
    features["pos_wordcount"] = pos_wordcount
    # features["emote_score"] = exp_count

    return features

def importing():

    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.corpus import twitter_samples
    from random import shuffle
    import re
    from statistics import mean
    from .models import Classifier
    
def main_training(extra_positive_data=[], extra_negative_data=[]):
    importing()
    
    # REMOVE AFTER!!!!!!!!!!!!!!!!!!!
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.corpus import twitter_samples
    from random import shuffle
    import re
    from statistics import mean
    from .models import Classifier
    # REMOVE AFTER!!!!!!!!!!!!!!!!!!!
    
    
    sia = SentimentIntensityAnalyzer()

    global counter
    counter = 0

    
    twitter_samples.fileids()
    global unwanted
    unwanted = nltk.corpus.stopwords.words("english")
    unwanted.extend([w.lower() for w in nltk.corpus.names.words()])


    neg_tweets = twitter_samples.strings('negative_tweets.json')
    neg_tweets += extra_negative_data
    # neg_tweets_exp_count = [find_expressions(tweet, sad_expressions) for tweet in neg_tweets]
    # neg_tweets = [remove_tweet_unwanted(tweet) for tweet in neg_tweets]

    pos_tweets = twitter_samples.strings('positive_tweets.json')
    pos_tweets += extra_positive_data
    # pos_tweets_exp_count = [find_expressions(tweet, happy_expressions) for tweet in pos_tweets]
    # pos_tweets = [remove_tweet_unwanted(tweet) for tweet in pos_tweets]

    all_tweets = neg_tweets + pos_tweets
    neg_tweet_words = []
    pos_tweet_words = []
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

    positive_fd = nltk.FreqDist(pos_tweet_words)
    negative_fd = nltk.FreqDist(neg_tweet_words)

    common_set = set(positive_fd).intersection(negative_fd)

    for word in common_set:
        del positive_fd[word]
        del negative_fd[word]

    top_100_positive = {word for word, count in positive_fd.most_common(100)}
    top_100_negative = {word for word, count in negative_fd.most_common(100)}

    shuffle(all_tweets)

    # for i in range(0,len(tweet_samp)): is_correct(tweet_samp[i],check_positive(tweet_samp[i]),pos_tweets)
    # print(f"Accuracy is: {counter/len(tweet_samp)}%")

    features = [
        (extract_features(tweet,top_100_positive,top_100_negative, sia),"pos")
        for tweet in pos_tweets
    ]
    features.extend([
        (extract_features(tweet,top_100_positive,top_100_negative, sia),"neg")
        for tweet in neg_tweets
    ])
    pass

    train_count = int(len(features) * (5/6))
    shuffle(features)
    classifier = nltk.NaiveBayesClassifier.train(features[:train_count])
    classifier.show_most_informative_features(10)
    print(nltk.classify.accuracy(classifier, features[train_count:]))
    date = datetime.datetime.date(datetime.datetime.now())
    classifier_name = f'classifier_{date}.pickle'
    a = Classifier(classifier_obj=classifier, classifier_date=date)
    a.save()

    return classifier_name, date
    