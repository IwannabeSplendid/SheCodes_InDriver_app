import requests

from src.settings import get_settings


settings = get_settings()


def share_ride_info(data, current_user):
    headers = {
        'Authorization': 'Bearer {settings.WHATSAPP_TOKEN}',
        'Content-Type': 'application/json',
    }

    json_data = {
        'messaging_product': 'whatsapp',
        'to': '{data.phone}',
        'type': 'template',
        'template': {
            'name': 'share_ride',
            'language': {
                'code': 'en_US',
            },
        },
    }

    response = requests.post('https://graph.facebook.com/v17.0/176017502259357/messages', headers=headers, json=json_data)
    return response.json()