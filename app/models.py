from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    country = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channelId = db.Column(db.String(255), unique=True, nullable=False)
    channelLink = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    createdAt = db.Column(db.DateTime, default=db.func.current_timestamp())

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
