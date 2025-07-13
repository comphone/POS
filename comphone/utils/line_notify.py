import requests
from flask import current_app

def send_line_notification(message):
    token = current_app.config.get('LINE_NOTIFY_TOKEN')
    if not token:
        print("LINE_NOTIFY_TOKEN not set.")
        return False
    
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'message': message
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error sending LINE notification: {e}")
        return False