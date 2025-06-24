import json
import os
from flask import Flask, jsonify
from policy_module.policy_manager import PolicyManager
from ppat_db.policy_db import save_policy_to_db

DATA_FILE = os.path.join(os.path.dirname(__file__), 'sample_data', 'policy_combined.json')

app = Flask(__name__)

@app.route('/parse-policy')
def parse_policy():
    """Parse sample policy and return groups and rules."""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        policy = json.load(f)
    manager = PolicyManager(policy, from_xml=False)
    manager.parse_lists()
    groups, rules = manager.parse_policy()
    return jsonify({
        'groups': groups,
        'rules': rules,
    })

@app.route('/save-policy')
def save_policy():
    """Parse sample policy and store results into SQLite DB."""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        policy = json.load(f)
    save_policy_to_db(policy)
    return jsonify({'status': 'saved'})

if __name__ == '__main__':
    app.run()
