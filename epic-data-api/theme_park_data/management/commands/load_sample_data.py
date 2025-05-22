import logging
import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime
from theme_park_data.models import (
    Park,
    Attraction,
    Show,
    AttractionStatus,
    ShowStatus,
    Showtime,
    OperatingHours,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load sample data for testing"

    def handle(self, *args, **options):
        try:
            self.stdout.write("Loading sample data...")

            # Create park
            park, created = Park.objects.update_or_create(
                id=uuid.UUID("12dbb85b-265f-44e6-bccf-f1faa17211fc"),
                defaults={
                    "name": "Universal's Epic Universe",
                    "entity_type": "PARK",
                    "timezone": "America/New_York",
                },
            )

            self.stdout.write(
                f"Park {'created' if created else 'updated'}: {park.name}"
            )

            # Create attractions
            attractions = [
                {
                    "id": "0c6a9af8-c006-4849-8475-1a6925e8f7d4",
                    "name": "Bowser Jr. Challenge",
                    "entity_type": "ATTRACTION",
                    "external_id": "24184",
                },
                {
                    "id": "43df71bf-aa7c-46c0-925c-46f69d8bf23f",
                    "name": "Mario Kart: Bowser's Challenge",
                    "entity_type": "ATTRACTION",
                    "external_id": "24130",
                },
                {
                    "id": "00feb57b-4fcc-48bc-9490-c9af71f30c1c",
                    "name": "Yoshi's Adventure",
                    "entity_type": "ATTRACTION",
                    "external_id": "24133",
                },
                {
                    "id": "447033ce-ee1f-4cca-bb12-47d22583ac12",
                    "name": "Stardust Racers",
                    "entity_type": "ATTRACTION",
                    "external_id": "24077",
                },
                {
                    "id": "dd8c015d-511f-47d4-b98b-18ce15735588",
                    "name": "Mine-Cart Madness",
                    "entity_type": "ATTRACTION",
                    "external_id": "24132",
                },
            ]

            attraction_objects = []
            for attraction_data in attractions:
                attraction, created = Attraction.objects.update_or_create(
                    id=uuid.UUID(attraction_data["id"]),
                    defaults={
                        "park": park,
                        "name": attraction_data["name"],
                        "entity_type": attraction_data["entity_type"],
                        "external_id": attraction_data["external_id"],
                    },
                )
                self.stdout.write(
                    f"Attraction {'created' if created else 'updated'}: {attraction.name}"
                )
                attraction_objects.append(attraction)

            # Create shows
            shows = [
                {
                    "id": "e3dd1ecd-f674-4aa7-83d9-9c7b4a8c886d",
                    "name": "The Untrainable Dragon",
                    "entity_type": "SHOW",
                    "external_id": "24137",
                },
                {
                    "id": "9c409ec9-a805-456c-96fc-d867cc5bc81b",
                    "name": "Le Cirque Arcanus",
                    "entity_type": "SHOW",
                    "external_id": "24110",
                },
            ]

            show_objects = []
            for show_data in shows:
                show, created = Show.objects.update_or_create(
                    id=uuid.UUID(show_data["id"]),
                    defaults={
                        "park": park,
                        "name": show_data["name"],
                        "entity_type": show_data["entity_type"],
                        "external_id": show_data["external_id"],
                    },
                )
                self.stdout.write(
                    f"Show {'created' if created else 'updated'}: {show.name}"
                )
                show_objects.append(show)

            # Create historical data for the past 24 hours
            now = timezone.now()

            # For each attraction, create 24 hourly status updates
            for attraction in attraction_objects:
                for i in range(24):
                    time_point = now - timedelta(hours=i)
                    status = (
                        "OPERATING" if i % 8 != 0 else "CLOSED"
                    )  # Every 8 hours, mark as closed

                    # Generate varying wait times (higher during peak hours)
                    hour = time_point.hour
                    if 10 <= hour <= 15:  # Peak hours
                        wait_time = 45 + (i % 5) * 20
                    else:
                        wait_time = 10 + (i % 5) * 10

                    if status == "CLOSED":
                        wait_time = None

                    AttractionStatus.objects.create(
                        attraction=attraction,
                        timestamp=time_point,
                        status=status,
                        standby_wait_time=wait_time,
                        single_rider_wait_time=(
                            wait_time // 2 if wait_time and wait_time > 20 else None
                        ),
                        last_updated=time_point,
                    )

            # For shows, create statuses and showtimes
            for show in show_objects:
                # Create hourly statuses
                for i in range(12):
                    time_point = now - timedelta(hours=i)
                    status = "OPERATING"

                    show_status = ShowStatus.objects.create(
                        show=show,
                        timestamp=time_point,
                        status=status,
                        last_updated=time_point,
                    )

                    # Add showtimes for the next 6 hours
                    for j in range(3):
                        start_time = time_point + timedelta(hours=j + 1)
                        end_time = start_time + timedelta(minutes=30)

                        Showtime.objects.create(
                            show_status=show_status,
                            type="Performance Time",
                            start_time=start_time,
                            end_time=end_time,
                        )

            self.stdout.write(self.style.SUCCESS("Successfully loaded sample data!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading sample data: {str(e)}"))
            logger.error(f"Error in load_sample_data command: {str(e)}")
