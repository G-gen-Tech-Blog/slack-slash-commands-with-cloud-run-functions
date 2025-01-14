# デプロイコマンド

```sh
PROJECT_ID="my-project"
SLACK_SIGNING_SECRET_PATH="projects/1234567890/secrets/slack-signing-secret"
SA_NAME="receive-slash-command"
function="receive-slash-command"
COMMAND_01="BACKEND_SAMPLE"
TOPIC_ID_01="backend-sample"
COMMAND_02="YOUR_ANOTHER_COMMAND"
TOPIC_ID_02="your-another-command"
 
gcloud functions deploy ${function} \
--gen2 \
--project=${PROJECT_ID} \
--region=asia-northeast1 \
--runtime=python312 \
--memory=256Mi \
--entry-point=main \
--trigger-http \
--allow-unauthenticated \
--service-account=${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com \
--set-secrets="SLACK_SIGNING_SECRET=${SLACK_SIGNING_SECRET_PATH}:latest" \
--set-env-vars "PROJECT_ID=${PROJECT_ID},TOPIC_ID_${COMMAND_01}=${TOPIC_ID_01},TOPIC_ID_${COMMAND_02}=${TOPIC_ID_02}"
```

# ローカルでのテスト手順

## ローカルでの仮想的な Cloud Run functions を起動

functinos-framework は pip install 済みの前提。

```sh
# ターミナルで実行
export TOPIC_ID_BACKEND_SAMPLE="backend-sample"
export PROJECT_ID="my-project"
functions-framework --debug --target main
```

## 仮想 function に curl でリクエストを送信

```sh
# 別ターミナルで実行
curl localhost:8080 \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "token=gIkuvaNzQIHg97ATvDxqgjtO\
&team_id=T0001\
&team_domain=example\
&enterprise_id=E0001\
&enterprise_name=Globular%20Construct%20Inc\
&channel_id=C2147483705\
&channel_name=test\
&user_id=U2147483697\
&user_name=Steve\
&response_url=https://hooks.slack.com/commands/1234/5678\
&trigger_id=13345224609.738474920.8088930838d88f008e0\
&api_app_id=A123456\
&command=/backend-sample\
&text=this-is-parameter\
&test_mode=True
"
```