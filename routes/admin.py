import random
import time
import string
from flask import Blueprint, redirect, url_for, render_template, request, jsonify, flash
from flask_login import login_user, logout_user, current_user, login_required

from models.connection import db
from models.model import User, VMRequest, VMConfig
from proxmoxer import ProxmoxAPI
from config import Config

app = Blueprint('admin', __name__)

@app.route('/dashboard')
def admin_dashboard():
    richieste = VMRequest.query.filter_by(status='pending').all()
    return render_template('admin/admin-dashboard.html', pending_requests=richieste)

@app.route('/approve-vm/<int:request_id>', methods=['POST'])
@login_required
def approve_vm(request_id):
    if current_user.role != 'admin':
        flash("Accesso negato: permessi insufficienti.")
        return redirect(url_for('default.home'))

    vm_req = VMRequest.query.get_or_404(request_id)
    if vm_req.status == 'pending':
        config = VMConfig.query.filter_by(name=vm_req.config_name).first()
        if not config:
            flash("Errore: Configurazione hardware non trovata.")
            return redirect(url_for('admin.admin_dashboard'))

        password = 'Password&1'
        new_vmid = 2800 + vm_req.id
        if new_vmid >= 2897:
            new_vmid = 2900 + vm_req.id
        node = Config.PROXMOX_NODE

        try:
            proxmox = ProxmoxAPI(
                Config.PROXMOX_HOST, 
                user=Config.PROXMOX_USER, 
                password=Config.PROXMOX_PASSWORD, 
                verify_ssl=Config.PROXMOX_VERIFY_SSL,
                timeout=300
            )

            template_id = int(config.image_id) 
            target_vmid = int(new_vmid)

            print(f"Clonazione in corso (Linked): {template_id} -> {target_vmid}...")
            proxmox.nodes(node).qemu(template_id).clone.post(
                newid=target_vmid,
                name=f"{vm_req.hostname}-{vm_req.id}",
                full=0,
                target=node
            )

            proxmox.nodes(node).qemu(new_vmid).config.post(
                cores=config.cpu,
                memory=config.ram, 
                cipassword=password,
                ciuser=vm_req.owner.username
                # ipconfig0=f"ip={ip_da_assegnare}/24,gw={gateway}"
            )

            proxmox.nodes(node).qemu(new_vmid).status.start.post()
            time.sleep(15) 
            ip_assegnato = "IP non ancora disponibile"
            
            try:
                net = proxmox.nodes(node).qemu(new_vmid).agent('network-get-interfaces').get()
                for iface in net.get('result', []):
                    for addr in iface.get('ip-addresses', []):
                        if addr.get('ip-address-type') == 'ipv4' and not addr['ip-address'].startswith('127'):
                            ip_assegnato = addr['ip-address']
                            break
            except Exception as e:
                print(f"Agent non ancora pronto: {e}")

            vm_req.status = 'created'
            vm_req.vm_id = new_vmid
            vm_req.ip_address = ip_assegnato
            vm_req.vm_user = 'root'
            vm_req.vm_password = password
            
            db.session.commit()
            flash(f"VM {vm_req.hostname} creata! ID: {new_vmid}, IP: {ip_assegnato}", "success")

        except Exception as e:
            db.session.rollback()
            print(f"Errore durante la creazione: {e}")
            flash(f"Errore critico durante la creazione su Proxmox: {str(e)}", "danger")

    else:
        flash("Questa richiesta è già stata elaborata.")

    return redirect(url_for('admin.admin_dashboard'))

@app.route('/reject-vm/<int:request_id>', methods=['POST'])
@login_required
def reject_vm(request_id):
    if current_user.role != 'admin':
        flash("Accesso negato.")
        return redirect(url_for('default.home'))

    vm_req = VMRequest.query.get_or_404(request_id)
    
    if vm_req.status == 'pending':
        vm_req.status = 'rejected'
        db.session.commit()
        flash(f"Richiesta per {vm_req.hostname} rifiutata.")
    
    return redirect(url_for('admin.admin_dashboard'))