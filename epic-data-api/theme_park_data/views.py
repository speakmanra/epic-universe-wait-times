from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Max, F, Q, Avg, Count
from django.db.models.functions import ExtractHour
from .models import Park, Attraction, Show, AttractionStatus, ShowStatus
import json
from datetime import timedelta


def index(request):
    """Home page view"""
    park = Park.objects.first()

    # Get latest attraction statuses
    attractions = (
        Attraction.objects.annotate(latest_status_time=Max("statuses__timestamp"))
        .prefetch_related("statuses")
        .order_by("name")
    )

    attraction_data = []
    for attraction in attractions:
        latest_status = attraction.statuses.filter(
            timestamp=attraction.latest_status_time
        ).first()

        if latest_status:
            attraction_data.append(
                {
                    "id": attraction.id,
                    "name": attraction.name,
                    "status": latest_status.status,
                    "standby_wait_time": latest_status.standby_wait_time,
                    "last_updated": latest_status.last_updated,
                }
            )

    # Get latest show statuses
    shows = (
        Show.objects.annotate(latest_status_time=Max("statuses__timestamp"))
        .prefetch_related("statuses")
        .order_by("name")
    )

    show_data = []
    for show in shows:
        latest_status = show.statuses.filter(timestamp=show.latest_status_time).first()

        if latest_status:
            # Get upcoming showtimes
            now = timezone.now()
            upcoming_showtimes = latest_status.showtimes.filter(
                start_time__gt=now
            ).order_by("start_time")[:5]

            show_data.append(
                {
                    "id": show.id,
                    "name": show.name,
                    "status": latest_status.status,
                    "upcoming_showtimes": [
                        st.start_time.strftime("%H:%M") for st in upcoming_showtimes
                    ],
                    "last_updated": latest_status.last_updated,
                }
            )

    context = {
        "park": park,
        "attractions": attraction_data,
        "shows": show_data,
        "current_time": timezone.now(),
    }

    return render(request, "theme_park_data/index.html", context)


def api_current_waits(request):
    """API endpoint for current wait times"""
    park = Park.objects.first()

    # Get all attractions with their latest status
    attractions = (
        Attraction.objects.annotate(latest_status_time=Max("statuses__timestamp"))
        .filter(
            Q(statuses__standby_wait_time__isnull=False)
            | Q(statuses__single_rider_wait_time__isnull=False)
        )
        .prefetch_related("statuses")
        .order_by("name")
    )

    data = {
        "park_name": park.name if park else "Unknown Park",
        "timestamp": timezone.now().isoformat(),
        "attractions": [],
    }

    for attraction in attractions:
        latest_status = attraction.statuses.filter(
            timestamp=attraction.latest_status_time
        ).first()

        if latest_status:
            data["attractions"].append(
                {
                    "id": str(attraction.id),
                    "name": attraction.name,
                    "status": latest_status.status,
                    "standby_wait_time": latest_status.standby_wait_time,
                    "single_rider_wait_time": latest_status.single_rider_wait_time,
                    "last_updated": (
                        latest_status.last_updated.isoformat()
                        if latest_status.last_updated
                        else None
                    ),
                }
            )

    return JsonResponse(data)


def attraction_detail(request, attraction_id):
    """View for showing detailed historical data about an attraction"""
    attraction = get_object_or_404(Attraction, id=attraction_id)

    # Get the latest status
    latest_status = (
        AttractionStatus.objects.filter(attraction=attraction)
        .order_by("-timestamp")
        .first()
    )

    # Get historical data for the past 24 hours
    now = timezone.now()
    past_24_hours = now - timedelta(hours=24)

    historical_statuses = AttractionStatus.objects.filter(
        attraction=attraction, timestamp__gte=past_24_hours
    ).order_by("timestamp")

    # Prepare chart data
    timestamps = []
    wait_times = []

    for status in historical_statuses:
        if status.standby_wait_time is not None:
            timestamps.append(status.timestamp.strftime("%H:%M"))
            wait_times.append(status.standby_wait_time)

    # Get hourly averages for the past 7 days
    past_7_days = now - timedelta(days=7)

    # Use a more compatible approach instead of .extra()
    hourly_data = (
        AttractionStatus.objects.filter(
            attraction=attraction,
            timestamp__gte=past_7_days,
            standby_wait_time__isnull=False,
        )
        .annotate(hour=ExtractHour("timestamp"))
        .values("hour")
        .annotate(avg_wait=Avg("standby_wait_time"))
        .order_by("hour")
    )

    hours = []
    avg_waits = []

    for data in hourly_data:
        hour = int(data["hour"])
        hours.append(f"{hour:02d}:00")
        avg_waits.append(round(data["avg_wait"], 1))

    context = {
        "attraction": attraction,
        "latest_status": latest_status,
        "historical_statuses": historical_statuses[:10],  # Most recent 10
        "chart_timestamps": json.dumps(timestamps),
        "chart_wait_times": json.dumps(wait_times),
        "hourly_chart_hours": json.dumps(hours),
        "hourly_chart_waits": json.dumps(avg_waits),
    }

    return render(request, "theme_park_data/attraction_detail.html", context)
