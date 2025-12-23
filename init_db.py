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
        VMConfig(name='Bronze', category='potenza', cpu=1, ram=2048, disk=20, image_id='template-101'),
        VMConfig(name='Silver', category='potenza', cpu=2, ram=4096, disk=40, image_id='template-102'),
        VMConfig(name='Gold',   category='potenza', cpu=4, ram=8192, disk=80, image_id='template-103')
    ]

    utilizzo = [
        VMConfig(name='Servizio', category='utilizzo', cpu=1, ram=1024, disk=10, image_id='template-201'),
        VMConfig(name='Generico', category='utilizzo', cpu=2, ram=4096, disk=30, image_id='template-202'),
        VMConfig(name='Desktop',  category='utilizzo', cpu=4, ram=6144, disk=50, image_id='template-203')
    ]

    for config in potenza + utilizzo:
        if not VMConfig.query.filter_by(name=config.name).first():
            db.session.add(config)

    db.session.commit()

