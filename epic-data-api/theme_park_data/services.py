import requests
import logging
import time
import json
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from .models import (
    Park,
    Attraction,
    Show,
    AttractionStatus,
    ShowStatus,
    Showtime,
    OperatingHours,
    ApiLog,
)

logger = logging.getLogger(__name__)


class ThemeParkApiService:
    """Service to interact with the theme park API"""

    def __init__(self):
        self.base_url = settings.THEME_PARK_API_BASE_URL
        self.entity_id = settings.THEME_PARK_ENTITY_ID

    def _log_api_call(
        self,
        endpoint,
        status_code=None,
        response_time=None,
        success=False,
        error_message=None,
    ):
        """Log API call to database"""
        ApiLog.objects.create(
            endpoint=endpoint,
            status_code=status_code,
            response_time=response_time,
            success=success,
            error_message=error_message,
        )

    def fetch_live_data(self):
        """Fetch live data from the API and process it"""
        endpoint = f"entity/{self.entity_id}/live"
        url = f"{self.base_url}/{endpoint}"

        start_time = time.time()
        try:
            response = requests.get(url)
            response_time = time.time() - start_time

            if response.status_code == 200:
                self._log_api_call(
                    endpoint=endpoint,
                    status_code=response.status_code,
                    response_time=response_time,
                    success=True,
                )
                data = response.json()
                self._process_park_data(data)
                return data
            else:
                self._log_api_call(
                    endpoint=endpoint,
                    status_code=response.status_code,
                    response_time=response_time,
                    success=False,
                    error_message=f"API returned status code {response.status_code}",
                )
                logger.error(
                    f"API request failed with status code {response.status_code}"
                )
                return None

        except Exception as e:
            response_time = time.time() - start_time
            self._log_api_call(
                endpoint=endpoint,
                response_time=response_time,
                success=False,
                error_message=str(e),
            )
            logger.error(f"API request failed with error: {str(e)}")
            return None

    def _parse_datetime(self, datetime_str):
        """Parse a datetime string into a datetime object"""
        if not datetime_str:
            return None
        try:
            # If datetime ends with Z (UTC), convert it to proper format
            if datetime_str.endswith("Z"):
                return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
            return datetime.fromisoformat(datetime_str)
        except (ValueError, TypeError):
            logger.warning(f"Could not parse datetime: {datetime_str}")
            return None

    def _process_park_data(self, data):
        """Process park data and save to database"""
        try:
            # Create or update park
            park, created = Park.objects.update_or_create(
                id=data["id"],
                defaults={
                    "name": data["name"],
                    "entity_type": data["entityType"],
                    "timezone": data["timezone"],
                },
            )

            # Process all live data items
            for item in data["liveData"]:
                if item["entityType"] == "ATTRACTION":
                    self._process_attraction(park, item)
                elif item["entityType"] == "SHOW":
                    self._process_show(park, item)
                else:
                    logger.warning(f"Unknown entity type: {item['entityType']}")

        except Exception as e:
            logger.error(f"Error processing park data: {str(e)}")

    def _process_attraction(self, park, item):
        """Process attraction data and save to database"""
        try:
            # Create or update attraction
            attraction, created = Attraction.objects.update_or_create(
                id=item["id"],
                defaults={
                    "park": park,
                    "name": item["name"],
                    "entity_type": item["entityType"],
                    "external_id": item.get("externalId"),
                },
            )

            # Create attraction status entry
            status_data = {
                "attraction": attraction,
                "status": item["status"],
                "last_updated": self._parse_datetime(item.get("lastUpdated")),
                "raw_data": item,
            }

            # Process queue data if available
            if "queue" in item:
                queue = item["queue"]
                if "STANDBY" in queue and queue["STANDBY"] is not None:
                    status_data["standby_wait_time"] = queue["STANDBY"].get("waitTime")

                if "SINGLE_RIDER" in queue and queue["SINGLE_RIDER"] is not None:
                    status_data["single_rider_wait_time"] = queue["SINGLE_RIDER"].get(
                        "waitTime"
                    )

            # Create attraction status
            attraction_status = AttractionStatus.objects.create(**status_data)

            # Process operating hours if available
            if "operatingHours" in item and item["operatingHours"]:
                for oh in item["operatingHours"]:
                    OperatingHours.objects.create(
                        attraction_status=attraction_status,
                        type=oh.get("type"),
                        start_time=self._parse_datetime(oh.get("startTime")),
                        end_time=self._parse_datetime(oh.get("endTime")),
                    )

        except Exception as e:
            logger.error(
                f"Error processing attraction {item.get('name', 'unknown')}: {str(e)}"
            )

    def _process_show(self, park, item):
        """Process show data and save to database"""
        try:
            # Create or update show
            show, created = Show.objects.update_or_create(
                id=item["id"],
                defaults={
                    "park": park,
                    "name": item["name"],
                    "entity_type": item["entityType"],
                    "external_id": item.get("externalId"),
                },
            )

            # Create show status entry
            show_status = ShowStatus.objects.create(
                show=show,
                status=item["status"],
                last_updated=self._parse_datetime(item.get("lastUpdated")),
                raw_data=item,
            )

            # Process showtimes if available
            if "showtimes" in item and item["showtimes"]:
                for st in item["showtimes"]:
                    Showtime.objects.create(
                        show_status=show_status,
                        type=st.get("type"),
                        start_time=self._parse_datetime(st.get("startTime")),
                        end_time=self._parse_datetime(st.get("endTime")),
                    )

        except Exception as e:
            logger.error(
                f"Error processing show {item.get('name', 'unknown')}: {str(e)}"
            )
