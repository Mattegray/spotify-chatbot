import sys
import os
import boto3


def main():
    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2', endpoint_url='http://dynamodb.ap-northeast-2.amazonaws.com')
    except:
        logging.error('Could not connect to DynamoDB')
        sys.exit(1)

    print("Success")
    sys.exit(0)


if __name__ == '__main__':
    main()
