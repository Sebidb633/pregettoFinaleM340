from flask import Blueprint, redirect, url_for, render_template, request, jsonify, flash
from flask_login import login_user, logout_user, current_user, login_required

from models.connection import db
from models.model import User, VMRequest, VMConfig
from proxmoxer import ProxmoxAPI
from config import Config

app = Blueprint('default', __name__)

@app.route('/')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    if current_user.role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif current_user.role == 'user':
        return redirect(url_for('default.request_vm'))

    return redirect(url_for('auth.login'))

@app.route('/request-vm', methods=['GET', 'POST'])
@login_required
def request_vm():
    return render_template('vm/request-new-vm.html')

@app.route('/requestNewVM', methods=['GET', 'POST'])
@login_required
def request_new():
    if request.method == 'POST':
        hostname = request.form.get('hostname')
        config_id = request.form.get('config_id')
        config = VMConfig.query.get(config_id)
        
        if config:
            new_request = VMRequest(
                user_id=current_user.id,
                config_name=config.name,
                hostname=hostname,
                status='pending'
            )

            db.session.add(new_request)
            db.session.commit()
            flash(f"Richiesta per {hostname} inviata con successo!")
            return redirect(url_for('default.request_vm'))

    configs_potenza = VMConfig.query.filter_by(category='potenza').all()
    return render_template('vm/vm-request.html',potenza=configs_potenza)

@app.route('/get-vm-ip/<int:vmid>', methods=['GET'])
@login_required
def get_vm_ip(vmid):
    node = Config.PROXMOX_NODE
    try:
        proxmox = ProxmoxAPI(
            Config.PROXMOX_HOST, 
            user=Config.PROXMOX_USER, 
            password=Config.PROXMOX_PASSWORD, 
            verify_ssl=Config.PROXMOX_VERIFY_SSL
        )
        
        status = proxmox.nodes(node).qemu(vmid).status.current.get()
        if status.get('status') != 'running':
            return jsonify({"ip": "VM Spenta", "details": "Avvia la VM su Proxmox"}), 202

        net = proxmox.nodes(node).qemu(vmid).agent('network-get-interfaces').get()
        for iface in net.get('result', []):
            for addr in iface.get('ip-addresses', []):
                if addr.get('ip-address-type') == 'ipv4' and not addr['ip-address'].startswith('127'):
                    new_ip = addr['ip-address']
                    vm_req = VMRequest.query.filter_by(vm_id=vmid).first()
                    if vm_req:
                        vm_req.ip_address = new_ip
                        db.session.commit()
                        
                    return jsonify({"ip": new_ip}), 200
        
        return jsonify({"ip": "In attesa...", "details": "Il DHCP non ha ancora assegnato l'IP"}), 202

    except Exception as e:
        return jsonify({"ip": "Agent non pronto", "details": str(e)}), 202

@app.route('/userForm')
def user_form_display():
    return render_template('userForm.html')

@app.route('/form', methods=['POST'])
def form_process():
    return "form process"

@app.route('/adduser', methods=['POST'])
def add_user():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "Utente creato con successo"}), 200
