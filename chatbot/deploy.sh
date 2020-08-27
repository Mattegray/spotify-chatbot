#!/bin/bash

rm *.zip
zip chatbot.zip -r *

aws s3 rm s3://matt-spotify-chatbot/chatbot.zip
aws s3 cp ./chatbot.zip s3://matt-spotify-chatbot/chatbot.zip
aws lambda update-function-code --function-name spotify-lambda --s3-bucket matt-spotify-chatbot --s3-key chatbot.zip
