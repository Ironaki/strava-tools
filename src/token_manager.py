import json
import logging
import time

import requests

from gcp_secret_manager import GCPSecretsManager

secret_manager = GCPSecretsManager()

logging.basicConfig(
    format="[%(levelname)s] - %(asctime)s.%(msecs)dZ - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class StravaTokens:
    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        expires_at: int,
        client_id: str,
        client_secret: str,
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at
        self.client_id = client_id
        self.client_secret = client_secret

    def serialize(self):
        return json.dumps(
            {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "expires_at": self.expires_at,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        )


def get_tokens():
    """Get strava tokens from Google Cloud Secret Manager, refresh if needed."""
    data = json.loads(secret_manager.access_secret_version("STRAVA_TOKENS"))
    strava_tokens = StravaTokens(
        data["access_token"],
        data["refresh_token"],
        data["expires_at"],
        data["client_id"],
        data["client_secret"],
    )
    # Refresh token if it has less than 5 min to expire
    if strava_tokens.expires_at - time.time() < 5 * 60:
        strava_tokens = refresh_access_token(strava_tokens)
    logger.info("Got Strava tokens")
    return strava_tokens


def refresh_access_token(old_strava_tokens: StravaTokens):
    # Call Strava API to refresh access token
    endpoint = "https://www.strava.com/oauth/token"
    resp = requests.post(
        endpoint,
        data={
            "client_id": old_strava_tokens.client_id,
            "client_secret": old_strava_tokens.client_secret,
            "refresh_token": old_strava_tokens.refresh_token,
            "grant_type": "refresh_token",
        },
    )
    resp_data = resp.json()
    new_strava_tokens = StravaTokens(
        resp_data["access_token"],
        resp_data["refresh_token"],
        resp_data["expires_at"],
        old_strava_tokens.client_id,
        old_strava_tokens.client_secret,
    )
    # Update Google Secret Manager
    secret_manager.add_secret_version("STRAVA_TOKENS", new_strava_tokens.serialize())
    logger.info("Refreshed Strava tokens")
    return new_strava_tokens
