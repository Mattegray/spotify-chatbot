import sys
sys.path.append('./libs')
import logging
import requests
import pymysql

PAGE_TOKEN = "EAAKf95XftI0BAD1rBPMRIi07ZBbIxJzajhZAcgAKalNYZApYeZBgAdQaUKVl53uMz6z7AUwvOhio7Y1VHC0cIsPZBmPCUuYF4quyycg5gOfpNSHOqZBBWJnBZBmput1F50Vh6RSIStA7loLqNBUseqqmpx6eeGXNyOWZAgQTcWX9uKo3n4OgU6VLNp6IZCdCbT6MZD"
VERIFY_TOKEN = "verify_123"

def lambda_handler(event, context):
    # event['params'] only exists for HTTPS GET

    if 'params' in event.keys():
        if event['params']['querystring']['hub.verify_token'] == VERIFY_TOKEN:
            return int(event['params']['querystring']['hub.challenge'])
        else:
            logging.error('Wrong validation token')
            raise SystemExit
    else:
        return None
