import os
from device_clients.skyhigh_client import SkyhighSWGClient
from ppat_db.policy_db import save_policy_to_db


def main():
    base_url = os.environ.get("SKYHIGH_URL")
    username = os.environ.get("SKYHIGH_USER")
    password = os.environ.get("SKYHIGH_PASS")

    if not all([base_url, username, password]):
        print("SKYHIGH_URL, SKYHIGH_USER, SKYHIGH_PASS environment variables required")
        return

    client = SkyhighSWGClient(base_url, username, password, verify_ssl=False)
    client.login()
    rulesets = client.list_rulesets(top_level_only=True)
    if not rulesets:
        print("No rulesets found")
        client.logout()
        return

    first = rulesets[0]
    xml_data = client.download_ruleset_xml(first['id'])

    save_policy_to_db(xml_data, from_xml=True)
    client.logout()
    print(f"Saved ruleset {first['title']} to database")


if __name__ == "__main__":
    main()
