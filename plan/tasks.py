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
    date_to_use = get_this_or_next_day()
    plan_dict = get_full_schedule(
        last_changed=date_to_use.last_updated if date_to_use else None
    )
    plan_changed = plan_dict.pop("changed")
    # Don't update db if the plan didn't change
    if not plan_changed:
        day = days.get(date=datetime.date.today())
        day.last_updated = datetime.datetime.now()
        day.save()
        return
    print("Plan data changed")
    info = plan_dict.pop("info")
    date = plan_dict.pop("date")
    last_changed = plan_dict.pop("last_changed")
    date_changed = True
    if days.count():  # If there is a day already
        date_changed = not days.filter(date=date)  # Does a day with this date exist already?
    if not days.count() or date_changed:
        # Create a new day object if it's the next day or there is no Day yet
        day = Day(date=date, last_changed=last_changed)
    else:
        # Modify the last day object with the current date
        day = days.get(date=date)
    day.info = info
    day.last_changed = last_changed
    day.last_updated = datetime.datetime.now()
    day.save()

    # Update db
    plans = []
    old_plans_for_day = list(Plan.objects.filter(day=day))
    for cls, periods in plan_dict.items():
        # Skip the data_changed dicts
        if cls.endswith("rooms") or cls.endswith("subjects"):
            continue
        new_plan = Plan.objects.create(cls=cls, day=day)
        plans.append(new_plan)
        for i, period in enumerate(periods):
            split_period = period.split()
            is_substituted = "für" in period or "statt" in period or "verlegt von" in period
            is_cancelled = "---" in period
            is_room_changed = plan_dict[cls + "rooms"][i]  # plan_dicts["9Brooms"][<period index>]
            is_subject_changed = plan_dict[cls + "subjects"][i]  # plan_dicts["9Bsubjects"][<period index>]
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
            if teacher_qs.exists():
                teacher = teacher_qs.first()
            else:
                teacher = Teacher.objects.create(short_name=teacher_short, last_name=teacher_short)

            Period.objects.create(
                plan=new_plan,
                number=number[:-1],
                room=room,
                teacher=teacher,
                subject=subject,
                is_substituted=is_substituted,
                is_cancelled=is_cancelled,
                is_room_changed=is_room_changed,
                is_subject_changed=is_subject_changed,
            )

    for old_plan in old_plans_for_day:
        old_plan.delete()


def get_this_or_next_day():
    datetime_today = datetime.datetime.today()

    # Check if today exists in the database
    this_day = Day.objects.filter(date=datetime_today)
    if this_day.exists():
        return this_day.first()

    # Check if there is a next day in the database
    higher_days = Day.objects.filter(date__gt=datetime_today)
    if higher_days.exists():
        return higher_days.first()

    return None
