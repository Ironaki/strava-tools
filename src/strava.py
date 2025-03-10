import json
import logging

import requests

from token_manager import get_tokens

STRAVA_API = "https://www.strava.com/api/v3"
TOKEN = get_tokens().access_token
HEADER = {"Authorization": f"Bearer {TOKEN}"}

logger = logging.getLogger(__name__)


def json_dump(file_name, data):
    with open(f"cache/{file_name}", "w") as f:
        json.dump(data, f, indent=4)
    return 0


class Activity:
    def __init__(self, activity_id, lazy=False):
        self.activity_id = activity_id
        if lazy:
            return
        self.activity = self.get_activity()
        self.device_name = self.activity.get("device_name", "UNKNOWN")
        self.distance = self.activity.get("distance", 0)
        self.private = self.activity["private"]
        self.commute = self.activity["commute"]
        self.hide_from_home = self.activity.get("hide_from_home", False)
        self.sport_type = self.activity["sport_type"]

    def print(self):
        return json.dumps(self.activity, indent=2)

    def __repr__(self):
        summary = (
            f"Summary of {self.activity_id}:\n"
            f"Device: {self.device_name}\n"
            f"Private: {self.private}\n"
            f"Commute: {self.commute}\n"
            "Use activity.print() to see full activity details"
        )
        return summary

    def get_activity(self):
        resp = requests.get(
            f"{STRAVA_API}/activities/{self.activity_id}", headers=HEADER
        )
        return resp.json()

    def update_activity(self, payload):
        resp = requests.put(
            f"{STRAVA_API}/activities/{self.activity_id}",
            headers=HEADER,
            json=payload,
        )
        return resp.json()

    def dump(self):
        return json_dump(f"activity_{self.activity_id}.json", self.activity)

    def get_link(self):
        return f"https://www.strava.com/activities/{self.activity_id}"

    def has_cadence(self):
        return "average_cadence" in self.activity


class ActivityList:
    def __init__(self):
        self.activity_list = self.get_activity_list()

    def get_activity_list(self):
        page = 1
        result = []
        while True:
            resp = requests.get(
                f"{STRAVA_API}/athlete/activities",
                headers=HEADER,
                params={"page": page, "per_page": 200},
            )
            page_result = resp.json()
            logger.debug(f"{len(page_result)}")
            if len(page_result) == 0:  # No more activities, break
                break
            result += page_result
            page += 1
        return result

    def dump(self):
        return json_dump("activity_list.json", self.activity_list)


class Gear:
    def __init__(self, gear_id):
        self.gear_id = gear_id
        self.gear = self.get_gear()

    def get_gear(self):
        resp = requests.get(f"{STRAVA_API}/gear/{self.gear_id}", headers=HEADER)
        return resp.json()

    def dump(self):
        return json_dump(f"gear_{self.gear_id}.json", self.gear)


class GearList:
    def __init__(self):
        self.gear_list = self.get_gear_list()

    def get_gear_list(self):
        resp = requests.get(f"{STRAVA_API}/athlete", headers=HEADER)
        return resp.json()["bikes"]

    def dump(self):
        return json_dump("gear_list.json", self.gear_list)


if __name__ == "__main__":
    # activity_list = ActivityList()
    # activity_list.dump()
    from src.const import GEAR_NAME_TO_ID_MAPPING

    activity = Activity(12528590242)
    print(activity)
    # activity.update_activity(
    #     {
    #         "hide_from_home": True,
    #         "commute": True,
    #         "gear_id": GEAR_NAME_TO_ID_MAPPING["FX 2020"],
    #     }
    # )
