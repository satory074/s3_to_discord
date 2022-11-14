import json
import math
import os

import requests

ACCOUNTID = os.environ["accountId"]
WEBHOOK_URL = os.environ["WebhookURL"]


def convert_size(size):
    """ Convert size to readable format """
    units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB")
    i = math.floor(math.log(size, 1024)) if size > 0 else 0
    size = round(size / 1024 ** i, 2)

    return f"{size} {units[i]}"


def lambda_handler(event, context):
    # event colors
    colors = {
        "ObjectCreated:CompleteMultipartUpload": 0x008000,
        "ObjectCreated:Put": 0x008000,
        "ObjectCreated:Post": 0x008000,
        "ObjectCreated:Copy": 0x008B8B,
        "ObjectRemoved:Delete": 0xFF6347,
        "ObjectRemoved:DeleteMarkerCreated": 0xFF6347,
    }

    for rec in event["Records"]:
        color = colors[rec["eventName"]] if rec["eventName"] in colors else 0x000000

        # Webhook data
        data = {
            "username": rec["eventSource"],
            "avatar_url": "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/main/dist/Storage/SimpleStorageService.png",
            "embeds": [
                {
                    "title": rec["s3"]["object"]["key"],
                    "description": convert_size(rec["s3"]["object"]["size"]),
                    "color": color,
                    "timestamp": rec["eventTime"],
                    "footer": {"text": rec["eventName"]},
                    "fields": [
                        {
                            "name": "awsRegion",
                            "value": rec["awsRegion"],
                            "inline": True,
                        },
                        {
                            "name": "bucket",
                            "value": rec["s3"]["bucket"]["name"],
                            "inline": True,
                        },
                    ],
                }
            ],
        }

        # POST
        requests.post(
            WEBHOOK_URL, json.dumps(data), headers={"Content-Type": "application/json"},
        )
