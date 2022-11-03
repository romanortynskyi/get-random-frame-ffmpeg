import json
import os
import boto3
from random import randint
import math

s3 = boto3.client('s3')

def convertMillis(millis):
    hours = (millis / (1000 * 60 * 60)) % 24
    minutes = (millis / (1000 * 60)) % 60
    seconds = (millis / 1000) % 60
    
    return {
        'hours': math.floor(hours),
        'minutes': math.floor(minutes),
        'seconds': math.floor(seconds)
    }

def format(hours, minutes, seconds):
    hoursStr = str(hours) if hours > 9 else '0' + str(hours)
    minutesStr = str(minutes) if minutes > 9 else '0' + str(minutes)
    secondsStr = str(seconds) if seconds > 9 else '0' + str(seconds)

    return hoursStr + ':' + minutesStr + ':' + secondsStr

def lambda_handler(event, context):
    body = json.loads(event['body'])
    print(body)

    bucket = 'video-app-2022'
    pathToFile = '/tmp/video.mp4'
    pathToSnapshot = '/tmp/frame.png'

    s3.download_file(bucket, body['name'], pathToFile)

    millis = randint(0, body['length'])
    
    convertedMillis = convertMillis(millis)

    formattedTime = format(convertedMillis['hours'], convertedMillis['minutes'], convertedMillis['seconds'])

    os.system('/opt/ffmpeg -ss ' + formattedTime + ' -i ' + pathToFile + ' -vframes 1 -q:v 2 ' + pathToSnapshot)

    object_name = os.path.splitext(body['name'])[0] + '.png'
    s3.upload_file(pathToSnapshot, bucket, object_name)

    return {
        'fileName': object_name,
        'src': 'https://' + bucket + '.s3.amazonaws.com/' + object_name
    }
