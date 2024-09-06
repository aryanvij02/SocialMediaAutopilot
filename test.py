
import requests

def send_slack_message(message):
    webhook_url = "https://hooks.slack.com/services/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"
    
    payload = {
        "text": message
    }
    
    response = requests.post(webhook_url, json=payload)
    
    if response.status_code == 200:
        print("Slack message sent successfully")
        return True
    else:
        print(f"Failed to send Slack message. Status code: {response.status_code}")
        return False     
    
    
if __name__ == "__main__":
    send_slack_message("testing again from code")