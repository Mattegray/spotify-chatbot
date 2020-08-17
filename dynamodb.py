import sys
import os
import boto3

def main():

    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')

if __name__=='main':
    main()
