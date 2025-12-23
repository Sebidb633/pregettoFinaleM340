import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager

from routes.default import app as bp_default
from routes.auth import app as bp_auth
from routes.admin import app as bp_admin

from models.connection import db
from models.model import User

app = Flask(__name__)
app.register_blueprint(bp_default)
app.register_blueprint(bp_auth, url_prefix='/auth')
app.register_blueprint(bp_admin, url_prefix='/admin')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', "sqlite:///progPx.db")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', "default_secret_key")

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user_callback(user_id):
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    return user

if __name__ == "__main__":
    app.run(debug=True)