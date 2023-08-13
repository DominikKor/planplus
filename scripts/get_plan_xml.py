import datetime
import os
from typing import Type

from django.db.models import Model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planplus.settings")
from pathlib import Path
from xml.etree import ElementTree

from dotenv import load_dotenv
import requests
import django
django.setup()
from plan.models import Day, Teacher, Plan, Period, FreeDay


def get_plan(date: datetime.datetime) -> Day:
    load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, ".env"))
    date_ymd = date.strftime("%Y%m%d")
    username = os.getenv("PLAN_USERNAME")
    password = os.getenv("PLAN_PASSWORD")
    plan_url = os.getenv("PLAN_URL")

    request = requests.get(f"https://{username}:{password}@{plan_url}PlanKl{date_ymd}.xml")
    if request.status_code != 200:
        raise ValueError("No file for this date")
    xml: ElementTree.Element = ElementTree.fromstring(request.text)

    last_changed = xml.find("Kopf").find("zeitstempel").text
    last_changed_date = datetime.datetime.strptime(last_changed, "%d.%m.%Y, %H:%M")

    this_days = Day.objects.filter(date=date)
    if this_days.exists():
        this_day = this_days.first()
        if not this_day.is_empty and this_day.last_changed == last_changed_date:
            this_day.last_updated = datetime.datetime.now()
            this_day.save()
            return this_day
        this_day.delete()

    free_days = xml.find("FreieTage").findall("ft")
    last_free_day_date = datetime.datetime.strptime(free_days[-1].text, "%y%m%d").date()
    if not FreeDay.objects.filter(date=last_free_day_date).exists():
        for free_day in free_days:
            FreeDay.objects.get_or_create(
                date=datetime.datetime.strptime(free_day.text, "%y%m%d").date(),
            )

    day = Day(
        info=xml.find("ZusatzInfo").find("ZiZeile").text,
        last_changed=last_changed_date,
        last_updated=datetime.datetime.now(),
        date=date,
        date_as_string=xml.find("Kopf").find("DatumPlan").text
    )

    all_plans = []
    all_periods = []
    for klass in xml.find("Klassen").findall("Kl"):
        plan = Plan(
            day=day,
            cls=klass.find("Kurz").text
        )

        for period_data in klass.find("Pl").findall("Std"):
            period = Period(
                plan=plan,
                number=int(period_data.find("St").text),
                subject=period_data.find("Fa").text,
                teacher=get_first_or_create(Teacher, short_name=period_data.find("Le").text),
                room=period_data.find("Ra").text,
                is_substituted=bool(period_data.find("Le").attrib.get("LeAe")),
                is_room_changed=bool(period_data.find("Ra").attrib.get("RaAe")),
                is_subject_changed=bool(period_data.find("Fa").attrib.get("FaAe")),
                is_cancelled=bool(period_data.find("Fa").attrib.get("FaAe")) == "---",
                change_info=period_data.find("If").text if period_data.find("If") is not None else None,
            )

            all_periods.append(period)

        all_plans.append(plan)

    day.save()
    Plan.objects.bulk_create(all_plans)
    Period.objects.bulk_create(all_periods)

    return day


def get_first_or_create(model: Type[Model], **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return model.objects.create(**kwargs)
    except model.MultipleObjectsReturned:
        return model.objects.filter(**kwargs).first()


if __name__ == '__main__':
    get_plan(datetime.datetime(2023, 6, 2))
