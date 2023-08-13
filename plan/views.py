import datetime
import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from scripts.get_plan_xml import get_plan
from .models import Day, Period, Teacher, FreeDay


def get_next_highest_day(date_obj):
    higher_days = Day.objects.filter(date__gte=date_obj)
    if higher_days.exists():
        day = higher_days.first()
    else:
        day = Day.objects.last()
    return day


def plan(request):
    date = request.GET.get("date")
    day = get_day(date)
    # If the user requests a day that doesn't exist yet, create it
    created_new_day = False
    if day is None:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        date_as_string = date_obj.strftime("%A, %d. %B %Y")
        day = Day(
            date=date_obj, last_updated=datetime.datetime.now(), last_changed=None, date_as_string=date_as_string,
            is_empty=True
        )
        day.save()
        created_new_day = True
    # Only re-fetch the plan if it's older than 1 minute
    if (day.last_updated < datetime.datetime.now() - datetime.timedelta(minutes=1)) or created_new_day:
        try:
            # Convert date to datetime, at midnight
            day = get_plan(datetime.datetime.combine(day.date, datetime.datetime.min.time()))
        except ValueError:
            pass
    return render(request, "plan/plan.html", {"plans": day.plans.all(), "day": day})


def get_day(date):
    if date:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        return Day.objects.filter(date=date_obj).first()
    else:
        try:
            day = Day.objects.get(date=datetime.datetime.today())
        except Day.DoesNotExist:
            day = get_next_highest_day(datetime.datetime.today())
    return day


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

    if action == "day-back":
        next_date = date - datetime.timedelta(days=1)
        while FreeDay.objects.filter(date=next_date).exists() or next_date.weekday() in [5, 6]:
            next_date -= datetime.timedelta(days=1)
    elif action == "day-forward":
        next_date = date + datetime.timedelta(days=1)
        while FreeDay.objects.filter(date=next_date).exists() or next_date.weekday() in [5, 6]:
            next_date += datetime.timedelta(days=1)
    else:
        next_date = None

    return HttpResponse(json.dumps({"success": True, "date": str(next_date)}))  # day-month-year

def russiagas(request):
    return render(request, "plan/russiagas.html")

def russiagas2(request):
    return render(request, "plan/russiagas2.html")


