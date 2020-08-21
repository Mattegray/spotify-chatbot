import sys
import os
import logging
import boto3
import requests
import base64
import json
import pymysql
from datetime import datetime


client_id = "0e757e773b7a40dfbdf63381d3169ddf"
client_secret = "59774097106141119b3ba074c69b99c9"

host = "fastcampus.crqhm4yzezxw.us-east-2.rds.amazonaws.com"
port = 3306
username = "matt"
database = "production"
password = "matt1234"


'''
Get artist_id from AWS RDS
Fetch data from Spotify using API
Get json format
Import to S3
'''


def main():
    try:
        conn = pymysql.connect(host, user=username, passwd=password, db=database, use_unicode=True, charset='utf8')
        cursor = conn.cursor()
    except:
        logging.error("Could not connect to RDS")
        sys.exit(1)

    headers = get_headers(client_id, client_secret)

    cursor.execute("SELECT id from artists")

    dt = datetime.utcnow().strftime("%Y-%m-%d")
    print(dt)
    sys.exit(0)

    with open('top_tracks.json', 'w') as f:
        for i in top_tracks:
            json.dump(i, f)
            f.write(os.linesep)

    s3 = boto3.resource('s3')
    object = s3.Object('matt-spotify-artists', 'dt={}/top-tracks.json'.format(dt))
    data = open('top-tracks.json', 'rb')
    object.put(Body=data)


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
