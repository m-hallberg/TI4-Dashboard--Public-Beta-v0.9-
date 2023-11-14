from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'soensdonttouch'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .game import game

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(game, url_prefix='/')

    from .models import Games, Players, Strats, Agendas, Nominations, Votes

    with app.app_context():
        db.create_all()

    return app

