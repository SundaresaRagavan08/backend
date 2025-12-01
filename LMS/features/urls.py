from django.urls import path
from .views import *

urlpatterns = [
    path('features/classes/', CreateClassView.as_view()),
    path('features/classes/<int:class_id>/', CourseForClassView.as_view()),
     
    path('features/students/<int:id>/', ClassStudentsView.as_view()),
    
    path('features/courses/', CoursesView.as_view()),
    path('features/courses/<int:id>/', SingleCoursesView.as_view()), 
    path('features/teachers/', TeacherView.as_view()),
]
