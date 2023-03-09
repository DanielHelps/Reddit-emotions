![reddit emotions logo](https://user-images.githubusercontent.com/101622750/177487525-497469fd-24a8-4c04-95c3-608d924cf38a.jpg)

# Reddit-emotions
## What is this repository?
This repository is the code for https://www.reddit-emotions.com. 

This web app checks reddit for a search term and gives an aggregated positivity score for the posts received contatining the search term.

![Happy and sad](https://user-images.githubusercontent.com/101622750/177492706-5392247e-188f-4494-9468-0d73b4669ec7.gif)

## Interesting... Tell me MORE!
Each search result is processed using a machine learning classifier, that determines the "positivity/negativity" of the result, and gives it a score between -1 (most negative) to +1 (most positive).
The average score of all the search results is then presented in the positivity meter.

![Reddit emotion results](https://user-images.githubusercontent.com/101622750/177497582-706c5265-9116-4fe7-b9b6-93b9acc8ed2e.gif)

## Cool! What else does it do?
The app also shows the 3 most positive (highest scores) results and the 3 most negative (lowest scores) results.
In addition, you can register and your searches and search results will be saved so you can look at them later. I also intend to add benefits to registered users (that will be applied retroactively) so it's worth registering!

![registered user](https://user-images.githubusercontent.com/101622750/177502852-08eba775-dc93-4521-9690-95319ec652e4.gif)

## Can I help train the classifier?
Yes! Click the "Train" button to get a random post from reddit and 3 buttons - "Positive", "Negative and "Neither". 
Click the "Positive" button if the sentence has positive vibes / feeling, and vice versa. 
If you are not sure whether the sentence qualifies as positive / negative then click the "Neither" button.
Once a week all the positive and negative posts will be gathered and the classifier will add them to the training process.
With your help, as time goes by, the classifier will become more and more accurate. :grinning:

![Training classifier](https://user-images.githubusercontent.com/101622750/177501430-dece408f-4a22-45cb-a5c9-c61573b94a24.gif)

## How can I run the code myself?
After cloning the repo, create the venv and install requirements. Then, download the nltk lexicon using the following commands in the shell:
```
$ import nltk
$ nltk.download('vader_lexicon')
```

Then use the following command in the terminal to run the server:
```
Python manage.py runserver
```

After that you need to open a second terminal and run celery for background tasks:
```
celery -A reddit_emotions worker -l info --pool=solo
```

Finally, you need to run celery beat in a third terminal for the periodic tasks:
```
celery -A reddit_emotions beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Then go to the following address:
```
http://127.0.0.1:8000/
```

If you want the server to listen to all network interfaces (and run it on different addresses at the same time), run the server using the following command instead:
```
Python manage.py runserver 0.0.0.0:8000
```

## Project roadmap

- [x] Core functionality coding
- [ ] Deployment
- [ ] Adding a wordcloud
- [ ] Decoupling frontend and backend (Django REST + react)
- [ ] Adding Love-Hate game
- [ ] Adding benefits to registered users




