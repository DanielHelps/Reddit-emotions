

# def importing():
import pickle
from typing import Tuple
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import re
from statistics import mean
from .classifier_functions import extract_features
from requests.auth import HTTPBasicAuth
import requests
from collections import Counter
import time
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp

def import_classifier():
    f = open('classifier.pickle', 'rb')
    classifier = pickle.load(f)
    f.close()
    return classifier


def import_top_100():
    import pickle
    f = open('top_100_neg.pickle', 'rb')
    top_100_neg = pickle.load(f)
    f.close()
    f = open('top_100_pos.pickle', 'rb')
    top_100_pos = pickle.load(f)
    f.close()
    return top_100_neg, top_100_pos


def classify_text(text: str, classifier, top_100_neg: list, top_100_pos: list, sia, count: int, pos_count: int) -> \
tuple[int, int]:
    features = extract_features(text, top_100_pos, top_100_neg, sia)
    if abs(features["mean_compound"]) > 0.5:
        print(text)
        print(features)
        count += 1
        if features["mean_compound"] > 0 or features["mean_positive"] > 0.2:
            pos_count += 1
    return count, pos_count


def get_results(param, headers, session, subreddit_check=False, past_results=[], specific_sub=None):
    results = []
    subreddits = []
    if specific_sub is None:
        res = session.get("https://oauth.reddit.com/search", params=param,
                           headers=headers)
    else:
        res = session.get(f"https://oauth.reddit.com/r/{specific_sub}/search", params=param,
                           headers=headers)
    post = res.json()['data']['children']
    after_value = res.json()['data']['after']
    count = len(post)
    for result in post:
        text = result['data']['title']
        if text not in past_results:
            results.append(text)
            if subreddit_check is True:
                subreddits.append(result['data']['subreddit'])
    print(f"{int(float(res.headers['x-ratelimit-remaining']))} requests remaining till end of period")
    print(f"{res.headers['x-ratelimit-reset']} seconds till period reset")
    if subreddit_check is True:
        return results, subreddits, after_value, count
    else:
        return results, after_value, count

def get_results_pushshift(param, session):
    
    # if specific_sub is None:
    res = session.get("https://api.pushshift.io/reddit/search/submission", params=param)
    # else:
        # res = session.get(f"https://oauth.reddit.com/r/{specific_sub}/search", params=param,
                        #    headers=headers)
    posts = res.json()
    titles= [x['title'] for x in posts['data']]
    # post = res.json()['data']['children']
    # after_value = res.json()['data']['after']
    # count = len(titles)
    # for text in titles:
    #     # text = result['data']['title']
    #     if text not in past_results:
    #         results.append(text)
    #         if subreddit_check is True:
    #             subreddits.append(result['data']['subreddit'])
    # print(f"{int(float(res.headers['x-ratelimit-remaining']))} requests remaining till end of period")
    # print(f"{res.headers['x-ratelimit-reset']} seconds till period reset")
    # if subreddit_check is True:
    #     return results, subreddits, after_value, count
    # else:
    return titles

def get_random_post():
    headers = get_oauth()
    res = requests.get("https://oauth.reddit.com/random", headers=headers)
    post_title = res.json()[0]['data']['children'][0]['data']['title']
    author = res.json()[0]['data']['children'][0]['data']['author']
    subreddit = res.json()[0]['data']['children'][0]['data']['subreddit_name_prefixed']
    # *****************
    return post_title, author, subreddit
    
    
async def fetch(session, param):
    async with session.get("https://api.pushshift.io/reddit/search/submission", params=param) as response:
        # print(f"{int(float(response.headers['x-ratelimit-remaining']))} requests remaining till end of period")
        # print(f"{response.headers['x-ratelimit-reset']} seconds till period reset")
        print("got results")
        return await response.json()
    
def get_oauth():
    auth = HTTPBasicAuth('vw-fkwBL0vnxGZ5Ofm5VKw', 'ULkWg9VlM0ObIqI1nDdtdVsFsmTG5Q')
    # auth = HTTPBasicAuth('classified', 'classified')

    # here we pass our login method (password), username, and password
    data = {'grant_type': 'password',
            'username': 'checking_sentiment',
            'password': '8S(pM;,E]crQQ{9:'}

    # data =  {'grant_type': 'password',
    #         'username': 'classified',
    #         'password': 'classified'}

    # setup our header info, which gives reddit a brief description of our app
    headers = {'User-Agent': 'sentiment_analysis_bot'}
    # send our request for an OAuth token
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)

    # convert response to JSON and pull access_token value
    TOKEN = res.json()['access_token']

    # add authorization to our headers dictionary
    headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

    # while the token is valid (~2 hours) we just add headers=headers to our requests
    requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

    return headers

async def by_aiohttp_concurrency(total, params, current_time, month_time):
    # use aiohttp
    titles = []
    session=aiohttp.ClientSession()
    tasks = []
    # url = "https://oauth.reddit.com/search"
    for i in range(total):
        params.update({"before":(current_time-i*month_time), "after":(current_time-(i+1)*month_time)})
        tasks.append(asyncio.create_task(fetch(session, params)))


    original_result = await asyncio.gather(*tasks)
    await session.close()
    for results_batch in original_result:
        titles += [x['title'] for x in results_batch['data']]
    
    return titles
    # for res in original_result:
    #     print(res)


def main(search_query):
    
    pos_counter = 0
    total_counter = 0
    classifier = import_classifier()
    top_100_neg, top_100_pos = import_top_100()
    sia = SentimentIntensityAnalyzer()
    # headers = get_oauth()
    search_term = search_query
    sort_type = "top"
    time_span = "month"
    parameters = {"restrict_sr": False, "limit": 100, "sort": sort_type, "q": search_term, "t": time_span}
    start_time = time.time()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = []
    subreddits = []
    subreddit_check = True
    listing_counter = 0
    # session = requests.Session()
    
    # import time
    current_time = int(time.time())
    month_time = 2592000
    results = []
    parameters = {"limit": 100, "sort": "top", "q": search_query}
    total = 6
    # for i in range(total):
        
        # results += asyncio.run(by_aiohttp_concurrency(total, parameters, headers))
    results = asyncio.run(by_aiohttp_concurrency(total,parameters,current_time,month_time))
    print("--- It took %s seconds ---" % (time.time() - start_time))

    
    
    
    
    
    
    
    
    
    # for i in range(0,3):
    #     if i == 0:
    #         results_add, subreddits_add, after, count = get_results(parameters, headers, session, subreddit_check, results)
    #     else:
    #         listing_counter += count
    #         parameters = {"restrict_sr": False, "limit": 100, "sort": sort_type, "q": search_term, "after": after,
    #                     "count": listing_counter, "t": time}
    #         results_add, subreddits_add, after, count = get_results(parameters, headers, session, subreddit_check, results)
    #     results += results_add
    #     subreddits += subreddits_add

    # # Adding common subreddits posts
    # common_subreddits = Counter(subreddits).most_common(10)
    # number_of_subs = 3
    # for sub in common_subreddits[0:number_of_subs]:
    #     sub_name = sub[0]
    #     parameters = {"restrict_sr": True, "limit": 100, "sort": sort_type, "q": search_term, "t": time}
    #     results_add, subreddits_add, after, count = get_results(parameters, headers, session, subreddit_check, results, specific_sub=sub_name)
    #     results += results_add

    for result in results:
        total_counter, pos_counter = classify_text(result, classifier, top_100_neg, top_100_pos, sia,
                                                   total_counter, pos_counter)

    if total_counter != 0:
        print(f"Positive score: {round(100*pos_counter/total_counter,2)}%")
        print(f"Most common subreddits (subreddit, number of mentions):")
        # print(common_subreddits)
        print("")

        # return ({round(100*pos_counter/total_counter,2)}, common_subreddits)
        return {round(100*pos_counter/total_counter,2)}
    else:
        return None
    


if __name__ == '__main__':
    main()
