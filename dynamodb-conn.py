import sys
import os
import boto3
import requests
import base64
import json
import logging
import pymysql
from boto3.dynamodb.conditions import Key, Attr

client_id = "0e757e773b7a40dfbdf63381d3169ddf"
client_secret = "59774097106141119b3ba074c69b99c9"

host = "fastcampus.crqhm4yzezxw.us-east-2.rds.amazonaws.com"
port = 3306
username = "matt"
database = "production"
password = "matt1234"


def main():
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2', endpoint_url='http://dynamodb.us-east-2.amazonaws.com')
    except:
        logging.error('Could not connect to DynamoDB')
        sys.exit(1)

    table = dynamodb.Table('top_tracks')

    query = table.query( # mostly used
        KeyConditionExpression=Key('artist_id').eq('00FQb4jTyendYWaN8pK0wa'),
        FilterExpression=Attr('popularity').gt(70)
    )

    scan = table.scan( # can be expensive
        FilterExpression=Attr('popularity').gt(70)
    )

    print(query['Items'])
    print(scan['Items'])
    print("Success")
    sys.exit(0)

    try:
        conn = pymysql.connect(host, user=username, passwd=password, db=database, use_unicode=True, charset='utf8')
        cursor = conn.cursor()
    except:
        logging.error("Could not connect to RDS")
        sys.exit(1)

    headers = get_headers(client_id, client_secret)

    cursor.execute("SELECT id FROM artists")

    for (artist_id, ) in cursor.fetchall():
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

    print("Success")
    sys.exit(0)



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
