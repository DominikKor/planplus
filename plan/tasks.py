from celery import shared_task
import datetime


@shared_task
def update_db():
    print("Updating db:", datetime.datetime.now())
    from plan.models import Period, Plan
    from scripts.main import get_plan
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
            if is_cancelled:  # Change field positions because of "---"
                subject = teacher
                teacher = extra[0 if not extra[0] == "Dr." else 1]  # Remove "Dr." from name
                room = ""
            Period.objects.create(plan=new_plan, number=number, room=room, teacher=teacher, subject=subject,
                                  is_substituted=is_substituted, is_cancelled=is_cancelled)

    for old_plan in old_plans:
        old_plan.delete()
