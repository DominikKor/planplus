from django.shortcuts import render

from scripts.main import get_plan
from .models import Plan, Period


def plan(request):
    plans = Plan.objects.all()
    return render(request, "plan/plan.html", {"plans": plans})


def update_db():
    plan_dict = get_plan(refresh=True)
    old_plans = list(Plan.objects.all())
    plans = []
    for cls, periods in plan_dict.items():
        new_plan = Plan.objects.create(cls=cls)
        plans.append(new_plan)
        for period in periods:
            is_substituted = "für" in period
            is_cancelled = "---" in period
            number, subject, teacher, room, *extra = period.split()
            if is_cancelled:
                subject = teacher
                teacher = extra[0 if not extra[0] == "Dr." else 1]
                room = ""
            Period.objects.create(plan=new_plan, number=number, room=room, teacher=teacher, subject=subject,
                                  is_substituted=is_substituted, is_cancelled=is_cancelled)

    for old_plan in old_plans:
        old_plan.delete()
