def initialize():
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    import re
    sia = SentimentIntensityAnalyzer()
    from statistics import mean


def is_wanted(word_tag_tuple: tuple, unwanted: list) -> bool:
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
