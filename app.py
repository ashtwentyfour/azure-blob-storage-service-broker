"""
Azure Blob Storage Service Broker
"""
import os, storage_account.manage, yaml
from flask import Flask, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()

with open(r'./config/settings.yml') as file:
    settings = yaml.load(file, Loader=yaml.FullLoader)

users = {
    "admin": generate_password_hash(os.environ['SERVICE_PASSWORD'])
}

@auth.verify_password
def verify_password(username, password):
    """Basic Broker Authentication"""
    if username in users and \
        check_password_hash(users.get(username), password):
        return username

@app.route('/health/ready')
@auth.login_required
def index():
    """Health Check"""
    return jsonify({"status": "UP"})

@app.route('/v2/catalog')
@auth.login_required
def catalog():
    """Catalog"""
    return jsonify(settings['catalog'])

@app.route('/v2/service_instances/<instance_id>', methods=['PUT'])
@auth.login_required
def create_service(instance_id):
    """Create Service Instance"""
    try:
        account_info = storage_account.manage.provision_account(instance_id)
        if account_info['exists']:
            return jsonify({"description": "account already exists"}), 409
        return jsonify({"dashboard_url": account_info['url']}), 201
    except Exception as err:
        print(err)
        return jsonify({"description": str(err)}), 502

@app.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['PUT'])
@auth.login_required
def bind_service(instance_id, binding_id):
    """Bind Service Instance"""
    try:
        account_creds = storage_account.manage.get_account_token(instance_id, binding_id)
        return jsonify({"credentials": account_creds}), 201
    except Exception as err:
        print(err)
        return jsonify({"description": str(err)}), 502

@app.route('/v2/service_instances/<instance_id>', methods=['DELETE'])
@auth.login_required
def delete_service(instance_id):
    """Delete Service Instance"""
    try:
        storage_account.manage.delete_account(instance_id)
        return jsonify({}), 200
    except Exception as err:
        print(err)
        return jsonify({"description": "error deleting storage account"}), 502

@app.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['DELETE'])
@auth.login_required
def unbind_service(instance_id, binding_id):
    """Unbind Service"""
    try:
        storage_account.manage.delete_container(instance_id, binding_id)
    except Exception as err:
        print(err)
        return jsonify({"description": "error deleting storage container"}), 502
    return jsonify({}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
    