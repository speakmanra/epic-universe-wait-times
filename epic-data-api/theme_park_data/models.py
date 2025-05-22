from django.db import models
from django.utils import timezone
import json


class Park(models.Model):
    """Theme park entity"""

    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=50)
    timezone = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Attraction(models.Model):
    """Attraction entity within a park"""

    id = models.UUIDField(primary_key=True)
    park = models.ForeignKey(Park, on_delete=models.CASCADE, related_name="attractions")
    name = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=50)
    external_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.name} at {self.park.name}"


class Show(models.Model):
    """Show entity within a park"""

    id = models.UUIDField(primary_key=True)
    park = models.ForeignKey(Park, on_delete=models.CASCADE, related_name="shows")
    name = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=50)
    external_id = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.name} at {self.park.name}"


class AttractionStatus(models.Model):
    """Historical record of attraction status"""

    attraction = models.ForeignKey(
        Attraction, on_delete=models.CASCADE, related_name="statuses"
    )
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50)
    standby_wait_time = models.IntegerField(null=True, blank=True)
    single_rider_wait_time = models.IntegerField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    raw_data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["attraction", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.attraction.name} - {self.status} - {self.timestamp}"


class ShowStatus(models.Model):
    """Historical record of show status"""

    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name="statuses")
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50)
    last_updated = models.DateTimeField(null=True, blank=True)
    raw_data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["show", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.show.name} - {self.status} - {self.timestamp}"


class Showtime(models.Model):
    """Individual showtime for a show"""

    show_status = models.ForeignKey(
        ShowStatus, on_delete=models.CASCADE, related_name="showtimes"
    )
    type = models.CharField(max_length=100, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.show_status.show.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class OperatingHours(models.Model):
    """Operating hours for an attraction"""

    attraction_status = models.ForeignKey(
        AttractionStatus, on_delete=models.CASCADE, related_name="operating_hours"
    )
    type = models.CharField(max_length=100, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["start_time"]
        verbose_name_plural = "Operating hours"

    def __str__(self):
        return f"{self.attraction_status.attraction.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class ApiLog(models.Model):
    """Log of API calls"""

    timestamp = models.DateTimeField(default=timezone.now)
    endpoint = models.CharField(max_length=255)
    status_code = models.IntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True)  # in seconds
    success = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.endpoint} - {self.timestamp} - {'Success' if self.success else 'Failed'}"
