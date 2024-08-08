from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
migrate = Migrate()
scheduler = BackgroundScheduler()

def create_app(config_class=Config):
    """
    创建 Flask 应用实例并配置应用、数据库和调度器。
    """
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)

    # 初始化数据库和迁移工具
    db.init_app(app)
    migrate.init_app(app, db)

    # 注册蓝图
    from app.views import bp as main_bp
    app.register_blueprint(main_bp)

    # 在应用上下文中启动调度器
    with app.app_context():
        from app.tasks import fetch_tweets
        scheduler.add_job(fetch_tweets, 'interval', hours=24, args=[app])
        scheduler.start()

    return app
