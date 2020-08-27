import sys
sys.path.append('./libs')
import logging
import requests
import pymysql
import messenger

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
        image_url, url = cursor.fetchall()[0]
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

        ## if artist not present add artist

        ##
