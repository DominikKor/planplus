from django.shortcuts import render

from .models import Day, Period


def plan(request):
    day = Day.objects.last()
    return render(request, "plan/plan.html", {"plans": day.plans.all(), "day": day})


def teacher(request, term: str):
    day = Day.objects.last()
    periods = Period.objects.filter(teacher=term, plan__day=day).order_by("number")
    periods = get_unique(periods)
    return render(request, "plan/plan.html", {"source": "Lehrer", "plans": [periods], "table_head": term, "day": day})


def room(request, term: str):
    day = Day.objects.last()
    periods = Period.objects.filter(room=term, plan__day=day).order_by("number")
    periods = get_unique(periods)
    return render(request, "plan/plan.html", {"source": "Raum", "plans": [periods], "table_head": term, "day": day})


def class_(request, term: str):
    day = Day.objects.last()
    periods = Period.objects.filter(plan__cls=term, plan__day=day).order_by("number")
    periods = get_unique(periods)
    return render(request, "plan/plan.html", {"source": "Klasse", "plans": [periods], "table_head": term, "day": day})


def search(request):
    term = request.GET.get("q")
    day = Day.objects.last()
    class_periods = Period.objects.filter(plan__cls__contains=term, plan__day=day).order_by("number")
    number_periods = Period.objects.filter(number__contains=term, plan__day=day).order_by("number")
    teacher_periods = Period.objects.filter(teacher__contains=term, plan__day=day).order_by("number")
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
