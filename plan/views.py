from django.shortcuts import render

from scripts.main import get_plan
from .models import Plan, Period


def plan(request):
    plans = Plan.objects.all()
    return render(request, "plan/plan.html", {"plans": plans})
