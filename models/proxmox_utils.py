from proxmoxer import ProxmoxAPI

def create_proxmox_vm():
    proxmox = ProxmoxAPI(
        "192.168.56.15",
        user="root@pam",
        token_name="flask-token",
        token_value="14aa7b54-8682-460b-b397-8dfcba1b205c",
        verify_ssl=False,
        timeout=60
    )