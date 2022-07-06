![reddit emotions logo](https://user-images.githubusercontent.com/101622750/177487525-497469fd-24a8-4c04-95c3-608d924cf38a.jpg)

# Reddit-emotions
## What is this repository?
This repository is the code for (**link**). 

This web app checks reddit for a search term and gives an aggregated positivity score for the posts received contatining the search term.
Each search result is processed using a machine learning classifier, that determines the "positivity/negativity" of the result, and gives it a score between -1 (most negative) to +1 (most positive).
The average score of all the search results is then presented in the positivity meter.


![Happy and sad](https://user-images.githubusercontent.com/101622750/177492706-5392247e-188f-4494-9468-0d73b4669ec7.gif)


## Cool! What else does it do?
The app also shows the 3 most positive (highest scores) results and the 3 most negative (lowest scores) results.
In addition, you can register and your searches and search results will be saved so you can look at them later. I also intend to add benefits to registered users (that will be applied retroactively) so it's worth registering!

## Can I help train the classifier?
Yes! Click the "Train" button to get a random post from reddit and 3 buttons - "Positive", "Negative and "Neither". 
Click the "Positive" button if the sentence has positive vibes / feeling, and vice versa. 
If you are not sure whether the sentence qualifies as positive / negative then click the "Neither" button.
Once a week all the positive and negative posts will be gathered and the classifier will add them to the training process.
With your help, as time goes by, the classifier will become more and more accurate. :grinning:

## How can I run the code myself?
After cloning the repo, use the following command to run the server:
```
Python manage.py runserver
```

Then you need to run celery for background tasks:
```
celery -A reddit_emotions worker -l info --pool=solo
```

Finally, you need to run celery beat for the periodic tasks:
```
celery -A reddit_emotions beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Then go to the following address:
```
http://127.0.0.1:8000/
```

If you want the server to be able to run on all IP, run the server using the following command instead:
```
Python manage.py runserver 0.0.0.0:8000
```

###### The smallest heading

Project roadmap:

- [x] Core functionality coding
- [ ] Deployment
- [ ] Adding a wordcloud
- [ ] Decoupling frontend and backend (Django REST + react)
- [ ] Adding Love-Hate game
- [ ] Adding benefits to registered users


![Desktop-2022 07 06-10 41 21 09](https://gifyu.com/image/SKIL1)
![Desktop-2022 07 06-10 41 21 09 (1)](https://user-images.githubusercontent.com/101622750/177497582-706c5265-9116-4fe7-b9b6-93b9acc8ed2e.gif)
![train gif](https://user-images.githubusercontent.com/101622750/177499347-77b82f2f-308b-46a5-8171-bf3fd2dfc2f2.gif)

