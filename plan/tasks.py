import datetime
import logging

import django
django.setup()

from celery import shared_task
from django.db.models import Q
from plan.models import Day, Plan, Period, Teacher

from scripts.get_plan import get_full_schedule, get_this_or_next_day


@shared_task
def update_db(force_update: bool = False) -> None:
    set_up_logger()
    logger = logging.getLogger("scripts")
    # Prepare day
    logger.info(f"Updating DB")
    date_to_use = get_this_or_next_day()
    plans_dict = get_full_schedule(
        last_changed=date_to_use.last_changed if date_to_use and not force_update else None
    )
    last_day = plans_dict["last_day"]
    current_day = plans_dict["current_day"]

    update_db_for_day_dict(last_day)
    update_db_for_day_dict(current_day)


def update_db_for_day_dict(day_dict: dict) -> None:
    logger = logging.getLogger("scripts")
    days = Day.objects.all()
    date = day_dict.pop("date")
    plan_changed = day_dict.pop("changed")
    # Don't update db if the plan didn't change
    if not plan_changed:
        day = days.get(date=date)
        day.last_updated = datetime.datetime.now()
        day.save()
        return
    info = day_dict.pop("info")
    last_changed = day_dict.pop("last_changed")
    date_changed = True
    if days.count():  # If there is a day already
        date_changed = not days.filter(date=date).exists()  # Does a day with this date exist already?
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
    for cls, periods in day_dict.items():
        # Skip the data_changed dicts
        if cls.endswith("rooms") or cls.endswith("subjects"):
            continue
        new_plan = Plan.objects.create(cls=cls, day=day)
        plans.append(new_plan)
        for i, period in enumerate(periods):
            split_period = period.split()
            is_substituted = "für" in period or "statt" in period or "verlegt von" in period
            is_cancelled = "---" in period
            is_room_changed = day_dict[cls + "rooms"][i]  # plan_dicts["9Brooms"][<period index>]
            is_subject_changed = day_dict[cls + "subjects"][i]  # plan_dicts["9Bsubjects"][<period index>]
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


def set_up_logger():
    # Set up logger
    from scripts.log import configure_logger
    logger = configure_logger("scripts")
    logger.debug("Set up logger")


if __name__ == '__main__':
    update_db()
