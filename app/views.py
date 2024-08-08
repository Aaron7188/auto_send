import chardet
import pandas as pd
from flask import Blueprint, request, jsonify, render_template
from app import db, scheduler
from app.models import User, Channel, Tweet
from app.utils import insert_users_to_db, insert_channels_to_db, send_message_to_channel
import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

def handle_uploaded_file(file):
    """
    处理上传的文件，支持CSV和Excel格式。
    """
    filename = file.filename
    if filename.endswith('.csv'):
        file_content = file.read()  # 读取文件内容
        result = chardet.detect(file_content)  # 检测文件编码
        file_encoding = result['encoding']  # 获取文件编码
        if not file_encoding:
            file_encoding = 'utf-8'  # 默认使用utf-8编码
        file.seek(0)  # 重置文件指针
        data = pd.read_csv(file, encoding=file_encoding)
    elif filename.endswith(('.xls', '.xlsx')):
        data = pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format")
    return data

@bp.route('/upload/users', methods=['POST'])
def upload_users():
    """
    处理用户文件上传并将用户数据插入数据库。
    """
    try:
        file = request.files['file']  # 获取上传的文件
        if not file:
            return jsonify({"message": "No file uploaded"}), 400

        data = handle_uploaded_file(file)  # 解析文件内容

        # 检查是否有预期的列
        if not all(column in data.columns for column in ['username', 'country', 'category']):
            return jsonify({"message": "Invalid file format"}), 400

        users = data[['username', 'country', 'category']].to_dict(orient='records')
        insert_users_to_db(users)  # 将用户数据插入数据库
        return jsonify({"message": "Users uploaded successfully"}), 200
    except Exception as e:
        # 记录错误日志
        print(f"Error uploading users: {e}")
        return jsonify({"message": "Failed to upload users"}), 500

@bp.route('/upload/channels', methods=['POST'])
def upload_channels():
    """
    处理频道文件上传并将频道数据插入数据库。
    """
    try:
        file = request.files['file']  # 获取上传的文件
        if not file:
            return jsonify({"message": "No file uploaded"}), 400

        data = handle_uploaded_file(file)  # 解析文件内容

        # 检查是否有预期的列
        if not all(column in data.columns for column in ['channelId', 'channelLink', 'country', 'category']):
            return jsonify({"message": "Invalid file format"}), 400

        channels = data[['channelId', 'channelLink', 'country', 'category']].to_dict(orient='records')
        insert_channels_to_db(channels)  # 将频道数据插入数据库
        return jsonify({"message": "Channels uploaded successfully"}), 200
    except Exception as e:
        # 记录错误日志
        print(f"Error uploading channels: {e}")
        return jsonify({"message": "Failed to upload channels"}), 500

@bp.route('/send-tweets', methods=['POST'])
def send_tweets():
    """
    处理发送推文的请求，根据选择的标签和数量，定时发送推文。
    """
    try:
        country = request.form.get('country')  # 获取选择的国家标签
        category = request.form.get('category')  # 获取选择的业务分类标签
        count = int(request.form['count'])  # 获取要发送的推文数量
        interval = int(request.form['interval'])  # 获取发送推文的时间间隔（小时）

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
    except Exception as e:
        # 记录错误日志
        print(f"Error sending tweets: {e}")
        return jsonify({"message": "Failed to send tweets"}), 500
