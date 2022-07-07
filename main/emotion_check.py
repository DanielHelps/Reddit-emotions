

from flask import session
from nltk.sentiment import SentimentIntensityAnalyzer
from .classifier_functions import extract_features
from requests.auth import HTTPBasicAuth
import requests
import time
import asyncio
import aiohttp
import operator


def import_top_100() -> list:
    """Imports the top 100 negative and top 100 positive words

    Returns:
        2 lists: top 100 negative and top 100 positive words
    """    
    import pickle
    f = open('top_100_neg.pickle', 'rb')
    top_100_neg = pickle.load(f)
    f.close()
    f = open('top_100_pos.pickle', 'rb')
    top_100_pos = pickle.load(f)
    f.close()
    return top_100_neg, top_100_pos

def check_sentence_list(method: str, sentence_list: list, sentence: tuple) -> list:
    """A function that creates a list of the most negative / positive sentences

    Args:
        method (str): "positive" to get the most positive sentences or anything else to get the most negative sentences
        sentence_list (list): the current list of the most positive / negative sentences
        sentence (tuple): the sentence to check (sentence string, score)

    Returns:
        list: the updated list with the most negative / positive sentences including the current sentence to check
    """    
    if len(sentence_list) < 3:
        sentence_list.append(sentence)
    else:
        if method == "positive":
            # Get the minimum of the score attribute in the list of tuples with the format [(sentence, score), (sentence, score), (sentence, score)]
            least_pos_sentence = min(sentence_list,key=operator.itemgetter(1))
            if sentence[1] > least_pos_sentence[1]:
                sentence_list.remove(least_pos_sentence)
                sentence_list.append(sentence)
        else:
            # Same as the positive list of sentences, just with negative scores
            least_neg_sentence = max(sentence_list,key=operator.itemgetter(1))
            if sentence[1] < least_neg_sentence[1]:
                sentence_list.remove(least_neg_sentence)
                sentence_list.append(sentence)
        
    return sentence_list


def classify_text(text: str, classifier, top_100_neg: list, top_100_pos: list, sia, count: int, pos_count: int, most_positive: list, most_negative: list) -> \
tuple[int, int]:
    features = extract_features(text, top_100_pos, top_100_neg, sia)
    min_mean_compound = 0.2
    if abs(features["mean_compound"]) > min_mean_compound:
        pos_or_neg = classifier.classify(extract_features(text, top_100_pos, top_100_neg, sia))
        print(text, f'!!!!!!{pos_or_neg.upper()}!!!!!!')
        count += 1
        if  pos_or_neg == 'pos':
            pos_count += 1

    
    # min_mean_compound = 0.4
    # if abs(features["mean_compound"]) > min_mean_compound:
    #     print(text)
    #     print(features)
    #     count += 1
    #     if features["mean_compound"] > 0 or features["mean_positive"] > 0.2:
    #         pos_count += 1
    check_sentence_list("positive",most_positive,(text, features["mean_compound"]))
    check_sentence_list("negative",most_negative,(text, features["mean_compound"]))
    pass
    return count, pos_count, most_positive, most_negative


def get_results_pushshift(param, session):
    
    res = session.get("https://api.pushshift.io/reddit/search/submission", params=param)
    posts = res.json()
    titles = [x['title'] for x in posts['data']]
    
    return titles

def get_random_post() -> list:
    """Generate a random reddit post for training purposes

    Returns:
        list: random post content, author of the post and subreddit
    """    
    headers = get_oauth()
    res = requests.get("https://oauth.reddit.com/random", headers=headers)
    post_title = res.json()[0]['data']['children'][0]['data']['title']
    author = res.json()[0]['data']['children'][0]['data']['author']
    subreddit = res.json()[0]['data']['children'][0]['data']['subreddit_name_prefixed']
    return post_title, author, subreddit
    
    
async def fetch(session: session, param: dict) -> dict:
    """ asynchronous function to get the results for the search term

    Args:
        session (session): the current session (important so no need to create connection again)
        param (dict): parameters to use in the API callout

    Returns:
        response: dictionary of the response (await)
    """    
    async with session.get("https://api.pushshift.io/reddit/search/submission", params=param) as response:
        print("got results")
        return await response.json()
    
def get_oauth():
    auth = HTTPBasicAuth('vw-fkwBL0vnxGZ5Ofm5VKw', 'ULkWg9VlM0ObIqI1nDdtdVsFsmTG5Q')

    # Pass login method (password), username, and password
    data = {'grant_type': 'password',
            'username': 'checking_sentiment',
            'password': '8S(pM;,E]crQQ{9:'}


    # Setup our header
    headers = {'User-Agent': 'sentiment_analysis_bot'}
    
    # Send our request for an OAuth token
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)

    # convert response to JSON and pull access_token value
    TOKEN = res.json()['access_token']

    # add authorization to our headers dictionary
    headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

    # # while the token is valid just add headers=headers to requests
    # requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

    return headers

async def by_aiohttp_concurrency(total, params, current_time, month_time):
    
    titles = []
    session=aiohttp.ClientSession()
    tasks = []
    for i in range(total):
        start_time = (current_time-(4*i+1)*month_time)
        end_time = (current_time-4*i*month_time)
        params.update({"before":end_time, "after":start_time})
        tasks.append(asyncio.create_task(fetch(session, params)))


    original_result = await asyncio.gather(*tasks)
    await session.close()
    for results_batch in original_result:
        titles += [x['title'] for x in results_batch['data']]
    titles = list(set(titles))
    return titles


def main(search_query):
    from .models import Classifier
    pos_counter = 0
    total_counter = 0
    classifier = Classifier.objects.latest('classifier_date').classifier_obj
    top_100_neg, top_100_pos = import_top_100()
    sia = SentimentIntensityAnalyzer()
    # search_term = search_query
    # sort_type = "top"
    # time_span = "month"
    # parameters = {"restrict_sr": False, "limit": 100, "sort": sort_type, "q": search_term, "t": time_span}
    start_time = time.time()
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # results = []

    current_time = int(time.time())
    month_seconds = 2592000
    results = []
    parameters = {"limit": 100,"sort":"desc", "sort_type": "score", "title":search_query}
    total = 10
    results = asyncio.run(by_aiohttp_concurrency(total, parameters, current_time, month_seconds))
    print("--- It took %s seconds ---" % (time.time() - start_time))

    most_positive = []
    most_negative = []
    for result in results:
        total_counter, pos_counter, most_positive, most_negative = classify_text(result, classifier, top_100_neg, top_100_pos, sia,
                                                   total_counter, pos_counter, most_positive, most_negative)

    if total_counter != 0:
        print(f"Positive score: {round(100*pos_counter/total_counter,2)}%")
        print(f"Most common subreddits (subreddit, number of mentions):")
        print("")

        return round(100*pos_counter/total_counter,2), most_positive, most_negative
    else:
        return None, [], []
    


if __name__ == '__main__':
    main()
