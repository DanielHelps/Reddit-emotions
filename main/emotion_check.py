

from flask import session
from nltk.sentiment import SentimentIntensityAnalyzer
from .classifier_functions import extract_features, main_training
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
    from main.models import top_100
    try:
        pos_100 = top_100.objects.latest('pos_date').top_obj
        neg_100 = top_100.objects.latest('neg_date').top_obj
    except:
        main_training()
        pos_100 = top_100.objects.latest('pos_date').top_obj
        neg_100 = top_100.objects.latest('neg_date').top_obj
    
    return neg_100, pos_100

def check_sentence_list(method: str, sentence_list: list, sentence: tuple) -> list:
    """A function that creates a list of the most negative / positive sentences including a sentence to check

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


def classify_text(text: str, top_100_neg: list, top_100_pos: list, sia, count: int, pos_count: int, most_positive: list, most_negative: list) -> tuple[int, int, list, list]:
    """Classfies text as positive or negative. Also checks for the most positive and most negative sentences.

    Args:
        text (str): text to check
        top_100_neg (list): top 100 negative words
        top_100_pos (list): top 100 positive words
        sia (sia object): sentiment intesity analyzer object
        count (int): current count of checked sentences 
        pos_count (int): current count of positive sentences
        most_positive (list): list of the current most positive sentences
        most_negative (list): list of the current most negative sentences

    Returns:
        tuple[int, int, list, list]: return the new total count and positive count, 
        also returns the most positive and most negative sentences including the new sentence
    """    
    from .models import Classifier
    try:
        classifier = Classifier.objects.latest('classifier_date').classifier_obj
    except:
        main_training()
        classifier = Classifier.objects.latest('classifier_date').classifier_obj

    # Extract features from text
    features = extract_features(text, top_100_pos, top_100_neg, sia)
    # Minimum absolute compound score to take into consideration (otherwise its too close to netural)
    min_mean_compound = 0.2
    if abs(features["mean_compound"]) > min_mean_compound:
        # Use classifier to decide whether sentence is positive or negative
        pos_or_neg = classifier.classify(extract_features(text, top_100_pos, top_100_neg, sia))
        print(text, f'!!!!!!{pos_or_neg.upper()}!!!!!!')
        count += 1
        if  pos_or_neg == 'pos':
            pos_count += 1
    # Check if sentence is one of the most positive (or negative)
    if features["mean_compound"] > 0:
        check_sentence_list("positive",most_positive,(text, features["mean_compound"]))
    else:
        check_sentence_list("negative",most_negative,(text, features["mean_compound"]))
    
    return count, pos_count, most_positive, most_negative


def get_random_post() -> tuple:
    """Generate a random reddit post for training purposes

    Returns:
        tuple: random post content, author of the post and subreddit
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
    
def get_oauth() -> dict:
    """Get authorization from reddit API so the user can fetch a random post

    Returns:
        dict: headers that include the access token
    """    
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

async def by_aiohttp_concurrency(total: int, params: dict, current_time: int, month_time: int) -> list:
    """An asynchronous function that uses a session to call the pushshift API multiple times,
    each time with different parameters (time range to search) in order to get different results each call.
    Eventually all results are gathered and returned

    Args:
        total (int): total amount of times to call the API
        params (dict): base parameters (not include time range) to use in the call of the API
        current_time (int): current time in epoch
        month_time (int): number of seconds in a month

    Returns:
        list: list of search results for the query in the parameters
    """    
    titles = []
    session=aiohttp.ClientSession()
    tasks = []
    # Add a different time range to search in each API call and create a task for it
    for i in range(total):
        start_time = (current_time-(4*i+1)*month_time)
        end_time = (current_time-4*i*month_time)
        params.update({"before":end_time, "after":start_time})
        tasks.append(asyncio.create_task(fetch(session, params)))

    # gather all the results from the API calls and close session
    original_result = await asyncio.gather(*tasks)
    await session.close()
    for results_batch in original_result:
        titles += [x['title'] for x in results_batch['data']]
    titles = list(set(titles))
    return titles


def main_check(search_query: str) -> tuple:
    """The main function that gets the emotion score for a search query

    Args:
        search_query (str): search query to check the score for

    Returns:
        tuple: emotion score, 3 most positive sentences, 3 most negative sentences
    """    
    # print(f'!!!!!!!!!{search_query}!!!!!!!!!!!')
    if isinstance(search_query, str) and search_query != None and search_query != '':
        pos_counter = 0
        total_counter = 0
        # Import latest top_100
        top_100_neg, top_100_pos = import_top_100()
        sia = SentimentIntensityAnalyzer()
    

        current_time = int(time.time())
        month_seconds = 2592000
        results = []
        # Create parameters for the pushshift API call
        parameters = {"limit":100, "sort":"desc", "sort_type":"score", "title":search_query}
        total = 10 # Total amount of times to call the API
        # Get results from "total" number of API calls
        results = asyncio.run(by_aiohttp_concurrency(total, parameters, current_time, month_seconds))

        most_positive = []
        most_negative = []
        # Classify the results as negative/positive and get the most negative/positive sentences
        for result in results:
            total_counter, pos_counter, most_positive, most_negative = classify_text(result, top_100_neg, top_100_pos, sia,
                                                    total_counter, pos_counter, most_positive, most_negative)

        if total_counter != 0:
            print(f"Positive score: {round(100*pos_counter/total_counter,2)}%")
            # print(f"Most common subreddits (subreddit, number of mentions):")
            # print("")

            return round(100*pos_counter/total_counter,2), most_positive, most_negative

        # If no results were found or search query is not string
    return None, [], []
    


if __name__ == '__main__':
    main_check()
