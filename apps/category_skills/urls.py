from django.urls import path
from . import views

app_name = 'category_skills'

urlpatterns = [
    path('' , views.CourseView , name="courses"),
    path('course_details/<int:skill_id>/' , views.CourseDetailView , name="course_details"),
    path('instructors/', views.InstructorView , name="instructors"),
    path('add_skill/<int:skill_id>/', views.add_skill_to_profile, name="add_skill"),
    path('remove_skill/<int:skill_id>/', views.remove_skill_from_profile, name="remove_skill"),
]