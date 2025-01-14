# デプロイコマンド

```sh
function=backend-sample
PROJECT_ID="my-project"
TOPIC_ID=backend-sample
TRIGGER_SA=receive-slash-command

gcloud functions deploy ${function} \
--gen2 \
--project=${PROJECT_ID} \
--region=asia-northeast1 \
--runtime=python312 \
--memory=128Mi \
--entry-point=main \
--trigger-topic=${TOPIC_ID} \
--trigger-service-account="${TRIGGER_SA}@${PROJECT_ID}.iam.gserviceaccount.com"
```