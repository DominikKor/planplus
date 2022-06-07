import datetime
import logging

import django
from celery import shared_task
from django.db.models import Q

# Only import models when NOT run as standalone script here, otherwise in the name-main if
if not __name__ == '__main__':
    from plan.models import Day, Plan, Period, Teacher

from scripts.get_plan import get_full_schedule


@shared_task
def update_db(force_update=False):
    set_up_logger()
    logger = logging.getLogger("scripts")
    # Prepare day
    logger.info(f"Updating DB")
    days = Day.objects.all()
    date_to_use = get_this_or_next_day()
    plan_dict = get_full_schedule(
        last_changed=date_to_use.last_changed if date_to_use and not force_update else None
    )
    plan_changed = plan_dict.pop("changed")
    # Don't update db if the plan didn't change
    if not plan_changed:
        date_to_use.last_updated = datetime.datetime.now()
        date_to_use.save()
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
                # Append as many "-" as needed
                needed_dashes = (4 - len(split_period)) * ["-"]
                split_period.extend(needed_dashes)
            try:
                number, subject, teacher_short, room, *extra = split_period
            except ValueError:
                print("Date:", date)
                print("Class:", cls)
                print("Period:", period)
                print(split_period)
                raise ValueError("not enough values to unpack (See print statements above for details)")
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


def set_up_logger():
    # Set up logger
    from scripts.log import configure_logger
    logger = configure_logger("scripts")
    logger.debug("Set up logger")


if __name__ == '__main__':
    django.setup()
    # Requires django.setup to be run first
    from plan.models import Day, Plan, Period, Teacher

    update_db()
