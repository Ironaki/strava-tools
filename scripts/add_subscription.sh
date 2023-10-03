http POST https://www.strava.com/api/v3/push_subscriptions \
  client_id="$CLIENT_ID" \
  client_secret="$CLIENT_SECRET" \
  callback_url="$CLOUD_FUNCTION_URL" \
  verify_token="$VERIFY_TOKEN"