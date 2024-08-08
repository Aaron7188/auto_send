from app import db
from app.models import User, Channel, Tweet
import telegram
from config import Config
import datetime
import asyncio
import httpx

# 初始化 Telegram 机器人
bot = telegram.Bot(token=Config.TELEGRAM_BOT_TOKEN)


def insert_users_to_db(users):
    """
    将用户数据插入数据库。

    Args:
        users (list): 包含用户数据的字典列表。
    """
    for user in users:
        if not User.query.filter_by(username=user['username']).first():
            new_user = User(username=user['username'], country=user['country'], category=user['category'])
            db.session.add(new_user)
    db.session.commit()


def insert_channels_to_db(channels):
    """
    将频道数据插入数据库。

    Args:
        channels (list): 包含频道数据的字典列表。
    """
    for channel in channels:
        if not Channel.query.filter_by(channelId=channel['channelId']).first():
            new_channel = Channel(channelId=channel['channelId'], channelLink=channel['channelLink'],
                                  country=channel['country'], category=channel['category'])
            db.session.add(new_channel)
    db.session.commit()


async def send_message(channel_id, text):
    """
    异步发送消息到指定频道。

    Args:
        channel_id (str): 频道ID。
        text (str): 要发送的消息内容。
    """
    try:
        await bot.send_message(chat_id=channel_id, text=text)
        print(f"Message sent to {channel_id}: {text}")
    except httpx.ConnectError as e:
        print(f"Failed to send message to {channel_id}: {e}")
    except Exception as e:
        print(f"Unexpected error sending message to {channel_id}: {e}")


def send_message_to_channel(tweet, channels, app):
    """
    发送消息到指定频道并更新数据库。

    Args:
        tweet (Tweet): 要发送的推文对象。
        channels (list): 包含频道对象的列表。
        app (Flask): Flask 应用实例。
    """
    with app.app_context():
        for channel in channels:
            try:
                # 使用新的会话发送消息
                with db.session() as session:
                    asyncio.run(send_message(channel.channelId, tweet.text))

                    # 更新推文状态为已发送
                    tweet.status = 'Sent'
                    tweet.sent_at = datetime.datetime.now()

                    session.add(tweet)
                    session.commit()
            except Exception as e:
                print(f"Failed to send message to {channel.channelId}: {e}")
                session.rollback()