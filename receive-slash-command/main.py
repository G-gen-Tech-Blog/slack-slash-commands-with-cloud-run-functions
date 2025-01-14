#!/usr/bin/env python3

import json
import logging
import os

import functions_framework
import google.cloud.logging
import google.cloud.pubsub_v1

from slack.signature import SignatureVerifier


# 標準 Logger の設定
logging.basicConfig(
        level=logging.INFO,
        format = "[%(asctime)s][%(levelname)s] receive-slash-command: %(message)s",
    )
logger = logging.getLogger()


# Cloud Logging ハンドラを logger に接続
logging_client = google.cloud.logging.Client()
logging_client.setup_logging()
logger.setLevel(logging.INFO)


# 環境変数の取得、Pub/Sub クライアントの生成
PROJECT_ID = os.environ.get("PROJECT_ID", None)
PUBSUB_CLIENT = google.cloud.pubsub_v1.PublisherClient()


# Slack からの署名を検証する関数
def verify_signature(request):
    request.get_data()

    verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])

    if not verifier.is_valid_request(request.data, request.headers):
        raise ValueError("Invalid request/credentials.")


@functions_framework.http
def main(request):
    # POST メソッド以外を拒否
    if request.method != "POST":
        logger.exception(f"POST リクエスト以外を受け付けました。")
        return "Method Not Allowed", 405

    try :
        verify_signature(request)
    except ValueError:
        # リクエストに test_mode 要素が含まれていたらスキップ
        if "test_mode" in request.form:
            logger.info("テストモードで実行")
            pass
        else:
            logger.exception("401 Unauthorized")
            return f"401 Unauthorized", 401
    except Exception as e:
        logger.exception(e)
        return f"500 Internal Server Error", 500

    # Slack からのリクエストを辞書型変数と JSON に格納
    body_dict = request.form.to_dict(flat=True)
    body_json = json.dumps(body_dict)
    logger.debug(body_json)

    # コマンド名に応じた環境変数から Pub/Sub トピック ID を取得
    command = body_dict["command"].lstrip("/").replace("-", "_").upper()
    ENV_NAME = f"TOPIC_ID_{command}"
    TOPIC_ID_FOR_COMMAND = os.environ.get(ENV_NAME, None)
    
    # 環境変数が定義されていない場合はエラー終了。Slack にメッセージを返すため 200 で終了
    if TOPIC_ID_FOR_COMMAND is None:
        logger.exception(f"環境変数 {ENV_NAME} が設定されていません。")
        return f":warning: コマンド {body_dict['command']} は未対応です。", 200

    # トピックのパスを生成
    TOPIC_PATH = PUBSUB_CLIENT.topic_path(PROJECT_ID, TOPIC_ID_FOR_COMMAND)

    try:
        # メッセージをパブリッシュ
        future = PUBSUB_CLIENT.publish(TOPIC_PATH, body_json.encode("utf-8"))
        logger.info(f"Pub/Sub message published: {future.result()}")
    except Exception as e:
        # Slack にメッセージを返すため 200 で終了
        logger.exception(e)  
        return f":bomb: 予期せぬエラーが発生しました。エラーメッセージ : {e}", 200

    # Slack に返答を返す
    return_messaage = f"処理を受け付けました。少々お待ち下さい。\n実行されたコマンド: {body_dict["command"]} {body_dict["text"]}"
    
    return return_messaage, 200