import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from app import db
from app.models import User, Tweet, UserUpdateCache

# 定义每批处理的用户数量
BATCH_SIZE = 1000

# 定义最大并发请求数
MAX_WORKERS = 10

def fetch_tweets_for_user(user, app):
    """
    获取单个用户的推文，并更新数据库。

    Args:
        user (User): 用户对象。
        app (Flask): Flask 应用实例，用于推送应用上下文。
    """
    # 推送 Flask 应用上下文
    with app.app_context():
        try:
            # 获取用户上次更新的时间
            user_cache = UserUpdateCache.query.filter_by(username=user.username).first()
            last_update = user_cache.last_update if user_cache else None

            # 定义 API 请求参数
            params = {}
            if last_update:
                params['since'] = last_update.strftime('%Y-%m-%dT%H:%M:%SZ')

            # 发送请求到 Twitter API 获取推文
            response = requests.get(f"https://api.geno.id/api/v2/twitter/tweets/by/username/{user.username}", params=params)
            if response.status_code == 200:
                tweets = response.json().get('data', [])
                for tweet in tweets:
                    # 检查推文是否已存在于数据库中
                    existing_tweet = Tweet.query.filter_by(tweetId=tweet['id']).first()
                    if not existing_tweet:
                        # 创建新的推文对象并添加到数据库
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

def fetch_tweets(app):
    """
    获取所有用户的推文，并更新数据库。

    Args:
        app (Flask): Flask 应用实例，用于推送应用上下文。
    """
    # 推送 Flask 应用上下文
    with app.app_context():
        # 获取所有用户
        users = User.query.all()
        total_users = len(users)

        # 使用线程池执行并发请求
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for i in range(0, total_users, BATCH_SIZE):
                # 将用户分批处理
                batch_users = users[i:i + BATCH_SIZE]
                futures = [executor.submit(fetch_tweets_for_user, user, app) for user in batch_users]

                # 处理每个批次的结果
                for future in as_completed(futures):
                    try:
                        future.result()  # 获取结果或处理异常
                    except Exception as e:
                        print(f"Error in future: {e}")
