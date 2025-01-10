import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#QRadar Notify Slack
#Version v0.1 by alan7s
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/xxxxxxxxxxx/xxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxx"
QRADAR_SEC_TOKEN = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
QRADAR_URL_BASE = "https://xxx.xx.x.xx"
REFERENCE_SET_ID = 100

def send_notification_to_slack(QRADAR_URL_BASE,id, description, offense_source, magnitude):
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Alert Offense #{id}",
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{description}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Alert details",
                    },
                    "value": "click_me_123",
                    "url": f"{QRADAR_URL_BASE}/console/qradar/jsp/QRadar.jsp?appName=Sem&pageId=OffenseSummary&summaryId={id}",
                    "action_id": "button-action"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Offense Source:* {offense_source}\n*Magnitude:* {magnitude}"
                    }
                ]
            }
        ]
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False


def get_offenses(qradar_url,qradar_header):
    try:
        response = requests.get(qradar_url, headers=qradar_header, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []
    
def get_notified_offenses(qradar_url,qradar_header):
    try:
        response = requests.get(qradar_url, headers=qradar_header, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []
    
def post_notified_offenses(qradar_url,qradar_header,offense_id):
    data = {
        "collection_id": REFERENCE_SET_ID,
        "value": f"{offense_id}"
    }
    try:
        response = requests.post(qradar_url, headers=qradar_header, json=data, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

def main():
    qradar_api_siem = QRADAR_URL_BASE + '/api/siem/offenses?filter=status%3Dopen'
    qradar_api_rdata = QRADAR_URL_BASE + '/api/reference_data_collections/set_entries?fields=value&filter=collection_id%3D' + str(REFERENCE_SET_ID)
    qradar_header = {
        'SEC':QRADAR_SEC_TOKEN,
        'Content-Type':'application/json',
        'Accept':'application/json'
    }

    notified_offenses = get_notified_offenses(qradar_api_rdata,qradar_header)
    offenses = get_offenses(qradar_api_siem,qradar_header)
    for offense in offenses:
        id = offense.get("id")
        magnitude = offense.get("magnitude")
        if magnitude > 5 and not any(notified_offense['value'] == f'{id:.1f}' for notified_offense in notified_offenses):
            description = offense.get("description")
            offense_source = offense.get("offense_source")
            if send_notification_to_slack(QRADAR_URL_BASE,id,description,offense_source,magnitude):
                post_notified_offenses(qradar_api_rdata,qradar_header,id)

if __name__ == "__main__":
    main()
