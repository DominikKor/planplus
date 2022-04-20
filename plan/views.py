import datetime
import json

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Day, Period, Teacher


def plan(request):
    date = request.GET.get("date")
    if date:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        day = get_object_or_404(Day, date=date_obj)
    else:
        day = Day.objects.last()
    return render(request, "plan/plan.html", {"plans": day.plans.all(), "day": day})


def teacher(request, term: str):
    day = get_current_day(request)
    teacher_obj = get_object_or_404(Teacher, short_name=term)
    periods = Period.objects.filter(teacher=teacher_obj, plan__day=day).order_by("number")
    periods = get_unique(periods)
    return render(request, "plan/plan.html", {"source": "Lehrer", "plans": [periods], "table_head": term, "day": day})


def room(request, term: str):
    day = get_current_day(request)
    periods = Period.objects.filter(room=term, plan__day=day).order_by("number")
    periods = get_unique(periods)
    return render(request, "plan/plan.html", {"source": "Raum", "plans": [periods], "table_head": term, "day": day})


def class_(request, term: str):
    day = get_current_day(request)
    periods = Period.objects.filter(plan__cls=term, plan__day=day).order_by("number")
    periods = get_unique(periods)
    return render(request, "plan/plan.html", {"source": "Klasse", "plans": [periods], "table_head": term, "day": day})


def search(request):
    term = request.GET.get("q")
    day = get_current_day(request)
    class_periods = Period.objects.filter(plan__cls__contains=term, plan__day=day).order_by("number")
    number_periods = Period.objects.filter(number__contains=term, plan__day=day).order_by("number")
    teacher_periods = Period.objects.filter(teacher__short_name__contains=term, plan__day=day).order_by("number")
    room_periods = Period.objects.filter(room__contains=term, plan__day=day).order_by("number")
    subject_periods = Period.objects.filter(subject__contains=term, plan__day=day).order_by("number")
    all_results = {
        "Klasse": class_periods,
        "Stunde": number_periods,
        "Lehrer": teacher_periods,
        "Raum": room_periods,
        "Unterricht": subject_periods
    }
    plans = {}
    for source, result in all_results.items():
        if result:
            result = get_unique(result)
            plans[source] = result
    return render(request, "plan/search_results.html",
                  {"source": "Suchen", "plans": plans, "table_head": term, "day": day})


def get_unique(periods):
    unique_periods = []
    for period in periods:
        if period not in unique_periods:
            if list(periods).count(period) == 4:
                period.plan.cls = period.plan.cls + "-D"
            unique_periods.append(period)
    return unique_periods


def get_current_day(request):
    date = request.GET.get("date")
    if date:
        day = get_object_or_404(Day, date=date)
    else:
        day = Day.objects.last()
    return day


@require_POST
@csrf_exempt
def find_next_date(request):
    date = datetime.datetime.strptime(request.POST["date"], "%d.%m.%Y").date()
    action = request.POST["action"]
    day = get_object_or_404(Day, date=date)
    next_day = day  # Should not matter, just for IDE
    if action == "day-back":
        if day == Day.objects.first():
            return HttpResponse(json.dumps({"success": False}))
        next_day = Day.objects.get(id=day.id-1)  # Get first Day with lower pk
    elif action == "day-forward":
        if day == Day.objects.last():
            return HttpResponse(json.dumps({"success": False}))
        next_day = Day.objects.get(id=day.id+1)  # Get first Day with higher pk
    print(f"Date: {date}, Action: {action}")
    return HttpResponse(json.dumps({"success": True, "date": str(next_day.date)}))  # day-month-year
