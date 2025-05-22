import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from theme_park_data.services import ThemeParkApiService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetch live data from the theme park API"

    def handle(self, *args, **options):
        service = ThemeParkApiService()

        try:
            self.stdout.write(f"Fetching live data at {timezone.now()}")
            data = service.fetch_live_data()

            if data:
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully fetched data for {data['name']}")
                )

                # Display some stats
                if "liveData" in data:
                    attractions = [
                        item
                        for item in data["liveData"]
                        if item["entityType"] == "ATTRACTION"
                    ]
                    shows = [
                        item
                        for item in data["liveData"]
                        if item["entityType"] == "SHOW"
                    ]

                    self.stdout.write(f"Processed {len(attractions)} attractions")
                    self.stdout.write(f"Processed {len(shows)} shows")

                    # Show attractions with wait times
                    self.stdout.write("\nCurrent wait times:")
                    for attraction in attractions:
                        if (
                            "queue" in attraction
                            and "STANDBY" in attraction["queue"]
                            and attraction["queue"]["STANDBY"]
                        ):
                            wait_time = attraction["queue"]["STANDBY"].get("waitTime")
                            if wait_time is not None:
                                self.stdout.write(
                                    f"{attraction['name']}: {wait_time} minutes"
                                )
            else:
                self.stdout.write(self.style.ERROR("Failed to fetch data from API"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            logger.error(f"Error in fetch_live_data command: {str(e)}")
