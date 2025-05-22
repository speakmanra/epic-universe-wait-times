from django.contrib import admin
from .models import (
    Park, Attraction, Show, AttractionStatus, ShowStatus, 
    Showtime, OperatingHours, ApiLog
)

@admin.register(Park)
class ParkAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity_type', 'timezone')
    search_fields = ('name',)


@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ('name', 'park', 'entity_type', 'external_id')
    list_filter = ('park', 'entity_type')
    search_fields = ('name',)


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('name', 'park', 'entity_type', 'external_id')
    list_filter = ('park', 'entity_type')
    search_fields = ('name',)


class OperatingHoursInline(admin.TabularInline):
    model = OperatingHours
    extra = 0


@admin.register(AttractionStatus)
class AttractionStatusAdmin(admin.ModelAdmin):
    list_display = ('attraction', 'status', 'standby_wait_time', 'single_rider_wait_time', 'timestamp', 'last_updated')
    list_filter = ('status', 'attraction', 'timestamp')
    search_fields = ('attraction__name',)
    date_hierarchy = 'timestamp'
    inlines = [OperatingHoursInline]


class ShowtimeInline(admin.TabularInline):
    model = Showtime
    extra = 0


@admin.register(ShowStatus)
class ShowStatusAdmin(admin.ModelAdmin):
    list_display = ('show', 'status', 'timestamp', 'last_updated')
    list_filter = ('status', 'show', 'timestamp')
    search_fields = ('show__name',)
    date_hierarchy = 'timestamp'
    inlines = [ShowtimeInline]


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('show_status', 'type', 'start_time', 'end_time')
    list_filter = ('show_status__show', 'type')
    date_hierarchy = 'start_time'


@admin.register(OperatingHours)
class OperatingHoursAdmin(admin.ModelAdmin):
    list_display = ('attraction_status', 'type', 'start_time', 'end_time')
    list_filter = ('attraction_status__attraction', 'type')
    date_hierarchy = 'start_time'


@admin.register(ApiLog)
class ApiLogAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'timestamp', 'status_code', 'response_time', 'success')
    list_filter = ('success', 'endpoint')
    search_fields = ('endpoint', 'error_message')
    date_hierarchy = 'timestamp'
