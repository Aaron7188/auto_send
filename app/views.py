from flask import Blueprint, request, jsonify, render_template
from app import db, scheduler
from app.models import User, Channel, Tweet
from app.utils import insert_users_to_db, insert_channels_to_db, send_message_to_channel
import datetime

# 创建蓝图，定义路由
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/upload/users', methods=['POST'])
def upload_users():
    """
    处理用户CSV文件上传并将用户数据插入数据库。
    """
    file = request.files['file']  # 获取上传的文件
    users = []
    for row in file:
        row = row.decode('utf-8').strip().split(',')
        users.append({'username': row[0], 'country': row[1], 'category': row[2]})
    insert_users_to_db(users)  # 将用户数据插入数据库
    return jsonify({"message": "Users uploaded successfully"}), 200

@bp.route('/upload/channels', methods=['POST'])
def upload_channels():
    """
    处理频道CSV文件上传并将频道数据插入数据库。
    """
    file = request.files['file']  # 获取上传的文件
    channels = []
    for row in file:
        row = row.decode('utf-8').strip().split(',')
        channels.append({'channelId': row[0], 'channelLink': row[1], 'country': row[2], 'category': row[3]})
    insert_channels_to_db(channels)  # 将频道数据插入数据库
    return jsonify({"message": "Channels uploaded successfully"}), 200

@bp.route('/send-tweets', methods=['POST'])
def send_tweets():
    """
    处理发送推文的请求，根据选择的标签和数量，定时发送推文。
    """
    country = request.form.get('country')  # 获取选择的国家标签
    category = request.form.get('category')  # 获取选择的业务分类标签
    count = int(request.form['count'])  # 获取要发送的推文数量
    interval = int(request.form['interval'])  # 获取发送推文的时间间隔

    # 查询满足条件的推文
    query = Tweet.query.filter_by(status='Pending')
    if country:
        query = query.filter_by(country=country)
    if category:
        query = query.filter_by(category=category)
    tweets = query.limit(count).all()

    # 查询满足条件的频道
    channels_query = Channel.query
    if country:
        channels_query = channels_query.filter_by(country=country)
    if category:
        channels_query = channels_query.filter_by(category=category)
    channels = channels_query.all()

    # 定时发送推文到相应的频道
    for i, tweet in enumerate(tweets):
        # 计算发送时间，interval是小时，所以乘以3600转换为秒
        send_time = datetime.datetime.now() + datetime.timedelta(seconds=interval * 3600 * i)
        scheduler.add_job(send_message_to_channel, 'date', run_date=send_time, args=[tweet, channels])

    return jsonify({"message": "Tweets are being sent"}), 200
