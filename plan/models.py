from django.db import models


class Plan(models.Model):
    cls = models.CharField(max_length=5)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Plan for {self.cls} on {self.datetime_updated}"


class Period(models.Model):
    plan = models.ForeignKey(Plan, related_name="periods", on_delete=models.CASCADE)
    number = models.CharField(max_length=5)  # What 45minute index? e.g. 1 => 8:10-8:55
    subject = models.CharField(max_length=10)
    teacher = models.CharField(max_length=5)  # max _should_ be 4 e.g. ("zzJz")
    room = models.CharField(max_length=5)
    is_substituted = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
