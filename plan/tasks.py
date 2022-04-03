from celery import shared_task
import datetime

from django.db.models import Q

from plan.models import Period, Plan, Day, Teacher
from scripts.get_plan import get_full_schedule


@shared_task
def update_db():
    # Prepare day
    print("Updating db:", datetime.datetime.now())
    days = Day.objects.all()
    plan_dict = get_full_schedule(last_changed=days.last().last_changed if days else None)
    plan_changed = plan_dict.pop("changed")
    # Don't update db if the plan didn't change
    if not plan_changed:
        day = days.last()
        day.last_updated = datetime.datetime.now()
        day.save()
        return
    print("Plan data changed")
    info = plan_dict.pop("info")
    date = plan_dict.pop("date")
    last_changed = plan_dict.pop("last_changed")
    date_changed = True
    if days.count():  # If there is a day already
        last_day = days.last()
        date_changed = last_day.date != date  # Does the existing day have the same date?
    if not days.count() or date_changed:
        # Create a new day object if there is a new date
        day = Day(date=date, last_changed=last_changed)
    else:
        # Modify the last day object with the current date
        day = days.last()
    day.info = info
    day.last_changed = last_changed
    day.last_updated = datetime.datetime.now()
    day.save()

    # Update db
    old_plans = list(Plan.objects.all())
    plans = []
    for cls, periods in plan_dict.items():
        new_plan = Plan.objects.create(cls=cls, day=day)
        plans.append(new_plan)
        for period in periods:
            split_period = period.split()
            is_substituted = "für" in period or "statt" in period or "verlegt von" in period
            is_cancelled = "---" in period
            if len(split_period) <= 3:  # If no room is provided
                split_period.append("-")
            number, subject, teacher_short, room, *extra = split_period
            if is_cancelled:  # Change field positions because of "---"
                subject = teacher_short
                # Remove "Dr." but leave "vom"
                if "vom" in extra and "Dr." in extra:
                    teacher_short = " ".join(extra[1:3])
                elif "vom" in extra:
                    teacher_short = " ".join(extra[0:2])
                elif "Dr." in extra:
                    teacher_short = extra[1]
                else:
                    teacher_short = extra[0]
                room = ""
            teacher_qs = Teacher.objects.filter(Q(short_name=teacher_short) | Q(last_name=teacher_short))
            if list(teacher_qs):
                teacher = teacher_qs.first()
            else:
                teacher = Teacher.objects.create(short_name=teacher_short, last_name=teacher_short)
            Period.objects.create(plan=new_plan, number=number[:-1], room=room, teacher=teacher, subject=subject,
                                  is_substituted=is_substituted, is_cancelled=is_cancelled)

    for old_plan in old_plans:
        old_plan.delete()
