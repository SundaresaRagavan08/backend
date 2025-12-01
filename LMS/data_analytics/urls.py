from django.urls import path
from .views import *

urlpatterns = [
    path('data/assignments/<int:course_id>/', AssignmentView.as_view(), name='assignments'),
    path('data/submissions/<int:course_id>/', SubmissionView.as_view(), name='submissions'),
    path('data/grade/<int:submission_id>/', GradeSubmissionView.as_view(), name='grade-submission'),
    path('data/attendance/<int:course_id>/', AttendanceView.as_view(), name='attendance'),
    path('data/dashboard/', DashboardDataView.as_view(), name='analytics-dashboard'),
]
