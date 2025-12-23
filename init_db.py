from app import app
from models.connection import db
from models.model import User, VMConfig

with app.app_context():

    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('admin')
        db.session.add(admin)

    potenza = [
        VMConfig(name='Bronze', cpu=1, ram=2048, disk=20, image_id='2800'),
        VMConfig(name='Silver', cpu=2, ram=4096, disk=40, image_id='2800'),
        VMConfig(name='Gold', cpu=4, ram=8192, disk=80, image_id='2800')
    ]

    db.session.commit()

