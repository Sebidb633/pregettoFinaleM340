from models.connection import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique = True, nullable = False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')
    vms = db.relationship('VMRequest', backref='owner', lazy=True)

    def set_password(self, password):
        """Imposta la password criptata."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se la password è corretta."""
        return check_password_hash(self.password_hash, password)
    
class VMConfig(db.Model):
    """Tabella per definire i template (Bronze, Silver, Gold)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    cpu = db.Column(db.Integer, nullable=False)
    ram = db.Column(db.Integer, nullable=False)
    disk = db.Column(db.Integer, nullable=False)
    image_id = db.Column(db.String(50), nullable=False)

class VMRequest(db.Model):
    """Tabella per gestire il workflow di approvazione e i dati di accesso finali"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    config_name = db.Column(db.String(50), nullable=False)
    hostname = db.Column(db.String(100), nullable=False)
    
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Dati restituiti dopo la creazione (Proxmox)
    vm_id = db.Column(db.Integer, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    vm_user = db.Column(db.String(50), nullable=True)
    vm_password = db.Column(db.String(100), nullable=True)
    ssh_key = db.Column(db.Text, nullable=True)