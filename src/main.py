import logging
import os
import threading

import functions_framework

ENV = os.environ.get("ENV", "dev")
with open("version.txt") as f:
    VERSION = f.read().strip()

if ENV == "prod":
    import google.cloud.logging

    client = google.cloud.logging.Client()
    client.setup_logging()
else:
    logging.basicConfig(
        format="[%(levelname)s] - %(asctime)s.%(msecs)dZ - %(name)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=logging.INFO,
    )

logger = logging.getLogger(__name__)


@functions_framework.http
def strava_webhook_trigger(request):
    """HTTP Cloud Function. Basically Flask.

    Strava's POST payload looks like this:
    {
        "aspect_type": "update",
        "event_time": 1516126040,
        "object_id": 1360128428,
        "object_type": "activity",
        "owner_id": 134815,
        "subscription_id": 120475,
        "updates": {
            "title": "Messy"
        }
    }

    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    """
    request_method = request.method

    if request_method == "POST":
        req_body = request.get_json()
        logger.info(f"POST Body: {req_body}")
        object_type, aspect_type = req_body["object_type"], req_body["aspect_type"]
        if object_type == "activity" and aspect_type == "create":
            activity_id = req_body["object_id"]
            threading.Thread(target=update_activity, args=(activity_id,)).start()
        else:
            logger.info("Skipped event")
        return {}, 200
    elif request_method == "GET":
        return {
            "message": "Healthy",
            "version": VERSION,
            "hub.challenge": request.args.get("hub.challenge"),
        }, 200
    else:
        return {"message": "Method not allowed"}, 405


def update_activity(activity_id):
    from const import GEAR_NAME_TO_ID_MAPPING
    from strava import Activity

    activity = Activity(activity_id)
    # If from Instinct, hide from home feed, mark as commute, and set gear
    if activity.device_name == "Garmin Instinct" and activity.sport_type == "Ride":
        activity.update_activity(
            {
                "hide_from_home": True,
                "commute": True,
                "gear_id": GEAR_NAME_TO_ID_MAPPING["FX 2020"],
            }
        )
        logger.info(f"Updated activity {activity_id} to commute.")
    # If from TrainerRoad, set gear
    elif activity.device_name == "TrainerRoad":
        activity.update_activity({"gear_id": GEAR_NAME_TO_ID_MAPPING["Kickr 2020"]})
        logger.info(f"Updated activity {activity_id} to TrainerRoad.")
