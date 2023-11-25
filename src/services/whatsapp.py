import requests

from src.settings import get_settings
from .security import get_current_client

settings = get_settings()


def share_ride_info(data, current_user, db):
    client = get_current_client(current_user)
    
    ride = db.table('rides').select('*').eq('id', data.ride_id).limit(1).execute().data[0]
    driver = db.table('drivers').select('*').eq('id', ride['driver_id']).limit(1).execute().data[0]
    car = db.table('cars').select('*').eq('id', driver['car_id']).limit(1).execute().data[0]

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
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": ride['pick_up_location'],
                        },
                        {
                            "type": "text",
                            "text": ride['start_time'].strftime("%d %B"),
                        },
                        {
                            "type": "text",
                            "text": ride['start_time'].strftime("%H:%M"),
                        },
                        {
                            "type": "text",
                            "text": ride['destination'],
                        },
                        {
                            "type": "text",
                            "text": driver['first_name'] + ' ' + driver['last_name'],
                        },
                        {
                            "type": "text",
                            "text": car['model'] + ' ' + car['color'],
                        },
                        {
                            "type": "text",
                            "text": car['plate_number'],
                        }
                    ]
                },
            ],
        },
    }

    json_data_v0 = {
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
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": data.ride_id,
                        }
                    ]
                }
            ]
        }
    }

    response = requests.post('https://graph.facebook.com/v17.0/176017502259357/messages', headers=headers, json=json_data_v0)
    return response.json()
