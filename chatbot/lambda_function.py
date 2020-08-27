import sys
sys.path.append('./libs')
import logging
import requests
import pymysql
import messenger
import json
import base64

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client_id = "0e757e773b7a40dfbdf63381d3169ddf"
client_secret = "59774097106141119b3ba074c69b99c9"

PAGE_TOKEN = "EAAKf95XftI0BAD1rBPMRIi07ZBbIxJzajhZAcgAKalNYZApYeZBgAdQaUKVl53uMz6z7AUwvOhio7Y1VHC0cIsPZBmPCUuYF4quyycg5gOfpNSHOqZBBWJnBZBmput1F50Vh6RSIStA7loLqNBUseqqmpx6eeGXNyOWZAgQTcWX9uKo3n4OgU6VLNp6IZCdCbT6MZD"
VERIFY_TOKEN = "verify_123"

host = "fastcampus.crqhm4yzezxw.us-east-2.rds.amazonaws.com"
port = 3306
username = "matt"
database = "production"
password = "matt1234"

try:
    conn = pymysql.connect(host, user=username, passwd=password, db=database, use_unicode=True, charset='utf8')
    cursor = conn.cursor()
except:
    logging.error("Could not connect to RDS")
    sys.exit(1)

bot = messenger.Bot(PAGE_TOKEN)


def lambda_handler(event, context):
    # event['params'] only exists for HTTPS GET

    if 'params' in event.keys():
        if event['params']['querystring']['hub.verify_token'] == VERIFY_TOKEN:
            return int(event['params']['querystring']['hub.challenge'])
        else:
            logging.error('Wrong validation token')
            raise SystemExit
    else:
        messaging = event['entry'][0]['messaging'][0]
        user_id = messaging['sender']['id']

        logger.info(messaging)
        artist_name = messaging['message']['text']

        query = "SELECT image_url, url FROM artists WHERE name = '{}'".format(artist_name)
        cursor.execute(query)
        raw = cursor.fetchall()

        if len(raw) == 0:
            text = search_artist(cursor, artist_name)
            bot.send_text(user_id, text)
            sys.exit(0)

        image_url, url = raw[0]
        payload = {
            'template_type': 'generic',
            'elements': [
                {
                    'title': 'Artist Info: {}'.format(artist_name),
                    'image_url': image_url,
                    'subtitle': 'information',
                    'default_action': {
                        'type': 'web_url',
                        'url': url,
                        'webview_height_ratio': 'full'
                    }
                }
            ]
        }
        bot.send_attachment(user_id, 'template', payload)

        query = "SELECT t2.genre FROM artists t1 JOIN artist_genres t2 ON t2.artist_id = t1.id WHERE t1.name = '{}'".format(artist_name)
        cursor.execute(query)

        genres = []
        for (genre, ) in cursor.fetchall():
            genres.append(genre)

        text = "Here are genres of {}".format(artist_name)
        bot.send_text(user_id, text)
        bot.send_text(user_id, ', '.join(genres))


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


def insert_row(cursor, data, table):
    placeholders = ', '.join(['%s'] * len(data))
    columns = ', '.join(data.keys())
    key_placeholders = ', '.join(['{0}=%s'.format(k) for k in data.keys()])
    sql = "INSERT INTO %s (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s" % (table, columns, placeholders, key_placeholders)
    cursor.execute(sql, list(data.values())*2)


def search_artist(cursor, artist_name):
    headers = get_headers(client_id, client_secret)
    params = {
        'q': artist_name,
        'type': 'artist',
        'limit': '1'
    }
    r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)
    raw = json.loads(r.text)

    if raw['artists']['items'] == []:
        return "Could not find the artist. Please try again."

    artist = {}
    artist_raw = raw['artists']['items'][0]
    if artist_raw['name'] == params['q']:
        artist.update(
            {
                'id': artist_raw['id'],
                'name': artist_raw['name'],
                'followers': artist_raw['followers']['total'],
                'popularity': artist_raw['popularity'],
                'url': artist_raw['external_urls']['spotify'],
                'image_url': artist_raw['images'][0]['url']
            }
        )

        for i in artist_raw['genres']:
            if len(artist_raw['genres']) != 0:
                insert_row(cursor, {'artist_id': artist_raw['id'], 'genre': i}, 'artist_genres')

        insert_row(cursor, artist, 'artists')
        conn.commit()

        return "We added the artist. Please try again in a second."

    return "Could not find the artist. Please try again."
