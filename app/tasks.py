import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from app import db
from app.models import User, Tweet, UserUpdateCache
from apscheduler.schedulers.background import BackgroundScheduler

# 初始化调度器
scheduler = BackgroundScheduler()

# 定义每批处理的用户数量
BATCH_SIZE = 1000

# 定义最大并发请求数
MAX_WORKERS = 10

def fetch_tweets_for_user(user):
    """获取单个用户的推文"""
    try:
        # 获取用户上次更新的时间
        user_cache = UserUpdateCache.query.filter_by(username=user.username).first()
        last_update = user_cache.last_update if user_cache else None

        # 定义API请求参数
        params = {}
        if last_update:
            params['since'] = last_update.strftime('%Y-%m-%dT%H:%M:%SZ')

        response = requests.get(f"https://api.geno.id/api/v2/twitter/tweets/by/username/{user.username}", params=params)
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
            # 更新用户的缓存时间
            if user_cache:
                user_cache.last_update = datetime.utcnow()
            else:
                new_cache = UserUpdateCache(username=user.username, last_update=datetime.utcnow())
                db.session.add(new_cache)
        db.session.commit()
    except Exception as e:
        print(f"Error fetching tweets for user {user.username}: {e}")

def fetch_tweets():
    """获取所有用户的推文"""
    users = User.query.all()
    total_users = len(users)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for i in range(0, total_users, BATCH_SIZE):
            batch_users = users[i:i + BATCH_SIZE]
            futures = [executor.submit(fetch_tweets_for_user, user) for user in batch_users]

            for future in as_completed(futures):
                try:
                    future.result()  # 处理结果或异常
                except Exception as e:
                    print(f"Error in future: {e}")

# 添加定时任务，每24小时运行一次fetch_tweets函数
scheduler.add_job(fetch_tweets, 'interval', hours=24)
# 启动调度器
scheduler.start()
