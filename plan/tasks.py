from celery import shared_task
import datetime

from django.db.models import Q

from plan.models import Period, Plan, Day, Teacher
from scripts.get_plan import get_plan


@shared_task
def update_db():
    print("Updating db:", datetime.datetime.now())
    plan_dict = get_plan()
    info = plan_dict.pop("info")
    date = plan_dict.pop("date")
    last_changed = plan_dict.pop("last_changed")
    Day.objects.all().delete()
    new_day = Day.objects.create(info=info, date=date, last_changed=last_changed)
    new_day.last_updated = datetime.datetime.now()
    new_day.save()
    old_plans = list(Plan.objects.all())
    plans = []
    for cls, periods in plan_dict.items():
        new_plan = Plan.objects.create(cls=cls, day=new_day)
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
