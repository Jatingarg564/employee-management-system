from django.urls import path

from apps.attendance.api.views import (
	CheckInAPIView,
	CheckOutAPIView,
	PauseAPIView,
	ResumeAPIView,
	TodayAttendanceAPIView,
)


urlpatterns = [
	path("check-in/", CheckInAPIView.as_view(), name="check-in"),
	path("pause/", PauseAPIView.as_view(), name="pause"),
	path("resume/", ResumeAPIView.as_view(), name="resume"),
	path("check-out/", CheckOutAPIView.as_view(), name="check-out"),
	path("today/", TodayAttendanceAPIView.as_view(), name="today"),
]