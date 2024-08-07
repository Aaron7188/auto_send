import requests
from app import db
from app.models import User, Tweet
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def fetch_tweets():
    users = User.query.all()
    for user in users:
        response = requests.get(f"https://api.geno.id/api/v2/twitter/tweets/by/username/{user.username}")
        if response.status_code == 200:
            tweets = response.json().get('data', [])
            for tweet in tweets:
                existing_tweet = Tweet.query.filter_by(tweetId=tweet['id']).first()
                if not existing_tweet:
                    new_tweet = Tweet(
                        tweetId=tweet['id'],
                        username=user.username,
                        text=tweet['text'],
                        tweetPictureLink=','.join(tweet.get('tweetPictureLink', [])),
                        tweetVideoLink=','.join(tweet.get('tweetVideoLink', [])),
                        tweetLink=tweet['tweetLink'],
                        createdAt=tweet['createdAt'],
                        lang=tweet['lang'],
                        replyToTweetId=tweet.get('replyToTweetId', ''),
                        status='Pending',
                        country=user.country,
                        category=user.category
                    )
                    db.session.add(new_tweet)
    db.session.commit()

scheduler.add_job(fetch_tweets, 'interval', hours=24)
scheduler.start()
