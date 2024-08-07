from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
migrate = Migrate()
scheduler = BackgroundScheduler()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import views
    app.register_blueprint(views.bp)

    from app.tasks import fetch_tweets
    scheduler.add_job(fetch_tweets, 'interval', hours=24)
    scheduler.start()

    return app
