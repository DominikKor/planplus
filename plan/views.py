from django.shortcuts import render

from .models import Plan, Period


def plan(request):
    plans = Plan.objects.all()
    return render(request, "plan/plan.html", {"plans": plans})


def teacher(request, term: str):
    periods = Period.objects.filter(teacher__equals=term).order_by("number")
    periods = get_unique(periods)
    return render(request, "plan/plan.html", {"source": "Lehrer", "plans": [periods], "table_head": term})


def room(request, term: str):
    periods = Period.objects.filter(room__equals=term).order_by("number")
    periods = get_unique(periods)
    return render(request, "plan/plan.html", {"source": "Räume", "plans": [periods], "table_head": term})


def class_(request, term: str):
    periods = Period.objects.filter(plan__equals=term).order_by("number")
    periods = get_unique(periods)
    return render(request, "plan/plan.html", {"source": "Klassen", "plans": [periods], "table_head": term})


def search(request):
    term = request.GET.get("q")
    class_periods = Period.objects.filter(plan__cls__contains=term).order_by("number")
    number_periods = Period.objects.filter(number__contains=term).order_by("number")
    teacher_periods = Period.objects.filter(teacher__contains=term).order_by("number")
    room_periods = Period.objects.filter(room__contains=term).order_by("number")
    subject_periods = Period.objects.filter(subject__contains=term).order_by("number")
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
    return render(request, "plan/search_results.html", {"source": "Suchen", "plans": plans, "table_head": term})


def get_unique(periods):
    unique_periods = []
    for period in periods:
        if period not in unique_periods:
            unique_periods.append(period)
    return unique_periods
