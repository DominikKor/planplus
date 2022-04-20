from django.urls import path

from plan import views

app_name = "plan"

urlpatterns = [
    path("", views.plan, name="plan"),
    path("teacher/<str:term>", views.teacher, name="teacher"),
    path("room/<str:term>", views.room, name="room"),
    path("class/<str:term>", views.class_, name="class"),
    path("search/", views.search, name="search"),
    path("_findnextdate/", views.find_next_date, name="find_next_date"),
]
