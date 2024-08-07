from flask import Blueprint, request, jsonify
from app import db, scheduler
from app.models import User, Channel, Tweet
from app.utils import insert_users_to_db, insert_channels_to_db, send_message_to_channel
import datetime

bp = Blueprint('main', __name__)

@bp.route('/upload/users', methods=['POST'])
def upload_users():
    file = request.files['file']
    users = []
    for row in file:
        row = row.decode('utf-8').strip().split(',')
        users.append({'username': row[0], 'country': row[1], 'category': row[2]})
    insert_users_to_db(users)
    return jsonify({"message": "Users uploaded successfully"}), 200

@bp.route('/upload/channels', methods=['POST'])
def upload_channels():
    file = request.files['file']
    channels = []
    for row in file:
        row = row.decode('utf-8').strip().split(',')
        channels.append({'channelId': row[0], 'channelLink': row[1], 'country': row[2], 'category': row[3]})
    insert_channels_to_db(channels)
    return jsonify({"message": "Channels uploaded successfully"}), 200

@bp.route('/send-tweets', methods=['POST'])
def send_tweets():
    country = request.form['country']
    category = request.form['category']
    count = int(request.form['count'])
    interval = int(request.form['interval'])

    tweets = Tweet.query.filter_by(country=country, category=category, status='Pending').limit(count).all()
    channels = Channel.query.filter_by(country=country, category=category).all()

    for i, tweet in enumerate(tweets):
        scheduler.add_job(send_message_to_channel, 'date', run_date=datetime.datetime.now() + datetime.timedelta(milliseconds=interval * i), args=[tweet, channels])

    return jsonify({"message": "Tweets are being sent"}), 200
