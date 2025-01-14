#!/usr/bin/env python3

import base64
import datetime
import json
import logging
import os
import requests 

import functions_framework
import google.cloud.logging


# 標準 Logger の設定
logging.basicConfig(
        level=logging.INFO,
        format = "[%(asctime)s][%(levelname)s] assign-support-engineers: %(message)s",
    )
logger = logging.getLogger()


# Cloud Logging ハンドラを logger に接続
logging_client = google.cloud.logging.Client()
logging_client.setup_logging()
logger.setLevel(logging.INFO)


@functions_framework.cloud_event
def main(cloud_event):
    # Pub/Sub から受け取ったメッセージの data を JSON として取得して辞書型に変換
    request = base64.b64decode(cloud_event.data["message"]["data"]).decode()
    request_dict = json.loads(request)

    logger.debug(request_dict)

    # リクエスト内容を変数に格納
    command = request_dict["command"]
    text = request_dict["text"]
    response_url = request_dict["response_url"]

    # Slack に返信するメッセージ内容
    post_text=f"あなたは {command} {text} を実行しましたね。受け取りました！"

    try:
        # response_url に対して返信
        headers = {'Content-type': 'application/json'}
        data = {'text': post_text}
        requests.post(response_url, headers=headers, data=json.dumps(data))

    except Exception as e:
        logger.exception(e)

    return "OK"