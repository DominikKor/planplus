from celery import shared_task
import datetime
from plan.models import Period, Plan, Day
from scripts.main import get_plan


@shared_task
def update_db():
    print("Updating db:", datetime.datetime.now())
    plan_dict = get_plan()
    info = plan_dict.pop("info")
    date = plan_dict.pop("date")
    last_updated = plan_dict.pop("last_updated")
    Day.objects.all().delete()
    new_day = Day.objects.create(info=info, date=date, last_updated=last_updated)
    old_plans = list(Plan.objects.all())
    plans = []
    for cls, periods in plan_dict.items():
        new_plan = Plan.objects.create(cls=cls, day=new_day)
        plans.append(new_plan)
        for period in periods:
            split_period = period.split()
            is_substituted = "für" in period
            is_cancelled = "---" in period
            if len(split_period) <= 3:  # If no room is provided
                split_period.append("-")
            number, subject, teacher, room, *extra = split_period
            if is_cancelled:  # Change field positions because of "---"
                subject = teacher
                teacher = extra[0 if not extra[0] == "Dr." else 1]  # Remove "Dr." from name
                room = ""
            Period.objects.create(plan=new_plan, number=number[:-1], room=room, teacher=teacher, subject=subject,
                                  is_substituted=is_substituted, is_cancelled=is_cancelled)

    for old_plan in old_plans:
        old_plan.delete()
