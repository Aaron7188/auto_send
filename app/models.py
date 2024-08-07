from app import db

#用户表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    country = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())

#频道表
class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channelId = db.Column(db.String(255), unique=True, nullable=False)
    channelLink = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())

#贴文表
class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tweetId = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    tweetPictureLink = db.Column(db.Text, nullable=True)
    tweetVideoLink = db.Column(db.Text, nullable=True)
    tweetLink = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())
    lang = db.Column(db.String(10), nullable=False)
    replyToTweetId = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum('Pending', 'Sent', 'Failed'), default='Pending')
    country = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)

#添加缓存表，存储每个用户上次更新推文的时间
class UserUpdateCache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    last_update = db.Column(db.DateTime)
