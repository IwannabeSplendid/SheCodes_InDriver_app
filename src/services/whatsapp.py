import requests

from src.settings import get_settings
from .security import get_current_client

settings = get_settings()


async def share_ride_info(data, current_user):
    client = get_current_client(current_user)

    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_TOKEN}',
        'Content-Type': 'application/json',
    }

    json_data = {
        'messaging_product': 'whatsapp',
        'to': f'7{data.phone}',
        'type': 'template',
        'template': {
            'name': 'share_ride',
            'language': {
                'code': 'en',
            },
            'components': [
                { 
                    "type": "HEADER",
                    "parameters": [{
                        "type": "text",
                        "text": client['first_name'],
                    }]
                },
                {
                    "type": "button",
                    "sub_type" : "url",
                    "index": "0", 
                    "parameters": [
                        {
                            "type": "text",
                            "text": data.ride_id,
                        }
                    ]
                },
            ],
        },
    }

    response = requests.post('https://graph.facebook.com/v17.0/176017502259357/messages', headers=headers, json=json_data)
    return response.json()
