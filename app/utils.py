from app import db
from app.models import User, Channel, Tweet
import telegram
from config import Config

bot = telegram.Bot(token=Config.TELEGRAM_BOT_TOKEN)

def insert_users_to_db(users):
    for user in users:
        if not User.query.filter_by(username=user['username']).first():
            new_user = User(username=user['username'], country=user['country'], category=user['category'])
            db.session.add(new_user)
    db.session.commit()

def insert_channels_to_db(channels):
    for channel in channels:
        if not Channel.query.filter_by(channelId=channel['channelId']).first():
            new_channel = Channel(channelId=channel['channelId'], channelLink=channel['channelLink'], country=channel['country'], category=channel['category'])
            db.session.add(new_channel)
    db.session.commit()

def send_message_to_channel(tweet, channels):
    for channel in channels:
        try:
            bot.send_message(chat_id=channel.channelId, text=tweet.text)
            tweet.status = 'Sent'
        except Exception as e:
            tweet.status = 'Failed'
            print(f"Error sending message: {e}")
    db.session.commit()
