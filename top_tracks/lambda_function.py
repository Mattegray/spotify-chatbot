import sys
sys.path.append('./libs')
import os
import boto3
import requests
import base64
import json
import logging


client_id = "0e757e773b7a40dfbdf63381d3169ddf"
client_secret = "59774097106141119b3ba074c69b99c9"

try:
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2', endpoint_url='http://dynamodb.us-east-2.amazonaws.com')
except:
    logging.error('Could not connect to DynamoDB')
    sys.exit(1)


def lambda_handler(event, context):
    headers = get_headers(client_id, client_secret)
    table = dynamodb.Table('top_tracks')
    artist_id = event['artist_id']
    URL = "https://api.spotify.com/v1/artists/{}/top-tracks".format(artist_id)
    params = {
        'country': 'US'
    }
    r = requests.get(URL, params=params, headers=headers)
    raw = json.loads(r.text)

    for track in raw['tracks']:
        data = {
            'artist_id': artist_id
        }
        data.update(track)
        table.put_item(
            Item=data
        )

    return "Success"


def get_headers(client_id, client_secret):
    endpoint = "https://accounts.spotify.com/api/token"
    encoded = base64.b64encode("{}:{}".format(client_id, client_secret).encode('utf-8')).decode('ascii')

    headers = {
        "Authorization": "Basic {}".format(encoded)
    }

    payload = {
        "grant_type": "client_credentials"
    }

    r = requests.post(endpoint, data=payload, headers=headers)

    access_token = json.loads(r.text)['access_token']

    headers = {
        "Authorization": "Bearer {}".format(access_token)
    }

    return headers


if __name__ == '__main__':
    main()
