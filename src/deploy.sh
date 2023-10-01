poetry export --without-hashes -f requirements.txt -o requirements.txt

gcloud beta functions deploy strava-updater \
  --gen2 \
  --runtime=python311 \
  --region=us-east4 \
  --source=. \
  --entry-point=strava_webhook_trigger \
  --trigger-http \
  --service-account cloud-function-strava-updater@main-pj-al.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --set-env-vars ENV=prod \
  --memory=512Mi \
  --cpu=0.583

rm requirements.txt