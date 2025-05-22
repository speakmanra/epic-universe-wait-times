from django.urls import path
from . import views

app_name = "theme_park_data"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/current-waits/", views.api_current_waits, name="api_current_waits"),
    path(
        "attraction/<uuid:attraction_id>/",
        views.attraction_detail,
        name="attraction_detail",
    ),
]
