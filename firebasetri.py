import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("iclaim-918b7-firebase-adminsdk-fpmv7-20c88a4f47.json")
firebase_admin.initialize_app(cred)

def send_to_token():
    # [START send_to_token]
    # This registration token comes from the client FCM SDKs.
    registration_token = 'c8TNUgONQ-myTWY96XVZ7F:APA91bEIRZ2-WM2DcGDFCT7L9r8_i_Y1Us6VMmzmO8FugrsJEokiKsvr9qvwily3IhgeU3qLE44jN7287xEpkKjft2Bj2cSf9NAuO9GQ3E_7Tqepqb5pBsX0LfUpYT3Ac625QzJ2p69Z'

    # See documentation on defining a message payload.
    message = messaging.Message(
        data={6
            'score': '850',
            'time': '2:45',
        },
        token=registration_token,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    # [END send_to_token]

send_to_token()