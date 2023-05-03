import datetime
import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Day, Period, Teacher


def get_fitting_date_if_not_exists(date_obj):
    higher_days = Day.objects.filter(date__gt=date_obj)
    if higher_days.exists():
        day = higher_days.first()
    else:
        day = Day.objects.last()
    return day


def plan(request):
    date = request.GET.get("date")
    if date:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        day = get_object_or_404(Day, date=date_obj)
    else:
        try:
            day = Day.objects.get(date=datetime.datetime.today())
        except Day.DoesNotExist:
            day = get_fitting_date_if_not_exists(datetime.datetime.today())
    return render(request, "plan/plan.html", {"plans": day.plans.all(), "day": day})


def teacher(request, term: str):
    day = get_current_day(request)
    teacher_obj = get_object_or_404(Teacher, short_name=term)
    periods = Period.objects.filter(teacher=teacher_obj, plan__day=day).order_by("number")
    periods = get_unique_periods(periods)
    return render(request, "plan/plan.html", {"source": "Lehrer", "plans": [periods], "table_head": term, "day": day})


def room(request, term: str):
    day = get_current_day(request)
    periods = Period.objects.filter(room=term, plan__day=day).order_by("number")
    periods = get_unique_periods(periods)
    return render(request, "plan/plan.html", {"source": "Raum", "plans": [periods], "table_head": term, "day": day})


def class_(request, term: str):
    day = get_current_day(request)
    periods = Period.objects.filter(plan__cls=term, plan__day=day).order_by("number")
    periods = get_unique_periods(periods)
    return render(request, "plan/plan.html", {"source": "Klasse", "plans": [periods], "table_head": term, "day": day})


def search(request):
    term = request.GET.get("q")
    day = get_current_day(request)
    class_periods = Period.objects.filter(plan__cls__contains=term, plan__day=day).order_by("number")
    number_periods = Period.objects.filter(number__contains=term, plan__day=day).order_by("number")
    teacher_periods = Period.objects.filter(
        Q(teacher__short_name__contains=term, plan__day=day) |
        Q(teacher__last_name__contains=term if len(term) >= 3 else "dontmatch", plan__day=day)
    ).order_by("number")
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
            result = get_unique_periods(result)
            plans[source] = result
    return render(request, "plan/search_results.html",
                  {"source": "Suchen", "plans": plans, "table_head": term, "day": day})


def get_unique_periods(periods):
    unique_periods = []
    for period in periods:
        if period not in unique_periods:
            if list(periods).count(period) == 4:
                period.plan.cls = period.plan.cls + "-D"  # Add "-D" to classes with courses (e. g. A-D)
            unique_periods.append(period)
    return unique_periods


def get_current_day(request):
    date = request.GET.get("date")
    if date:
        return get_object_or_404(Day, date=date)
    try:
        day = Day.objects.get(date=datetime.date.today())
    except Day.DoesNotExist:
        day = Day.objects.last()
    return day


@require_POST
@csrf_exempt
def find_next_date(request):
    date = datetime.datetime.strptime(request.POST["date"], "%d.%m.%Y").date()
    action = request.POST["action"]
    day = get_object_or_404(Day, date=date)
    next_day = None
    days = Day.objects.order_by("date")
    day_index = list(days).index(day)

    if action == "day-back":
        if day == days.first():
            return HttpResponse(json.dumps({"success": False}))
        next_day = days[day_index - 1]
    elif action == "day-forward":
        if day == days.last():
            return HttpResponse(json.dumps({"success": False}))
        next_day = days[day_index + 1]

    print(f"Date: {date}, Action: {action}")
    return HttpResponse(json.dumps({"success": True, "date": str(next_day.date)}))  # day-month-year

def russiagas(request):
    return render(request, "plan/russiagas.html")

def russiagas2(request):
    return render(request, "plan/russiagas2.html")


