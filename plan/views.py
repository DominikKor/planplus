from django.shortcuts import render

from scripts.get_raw_plan_dict import get_plan


def plan(request):
    plan_dict = get_plan()
    return render(request, "plan/plan.html", {"plan_dict": plan_dict})
