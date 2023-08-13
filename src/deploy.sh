poetry export --without-hashes -f requirements.txt -o requirements.txt

gcloud functions deploy strava-updater \
  --gen2 \
  --runtime=python311 \
  --region=us-west1 \
  --source=. \
  --entry-point=strava_webhook_trigger \
  --trigger-http \
  --service-account cloud-function-strava-updater@main-pj-al.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --set-env-vars ENV=prod \
  --memory=192Mi

rm requirements.txt