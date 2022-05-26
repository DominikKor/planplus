from django.db import models


class Day(models.Model):
    info = models.CharField(max_length=10000, null=True, blank=True)
    last_changed = models.DateTimeField()
    last_updated = models.DateTimeField(auto_now_add=True)
    date = models.DateField()

    def __str__(self):
        return f"Day {self.date}"


class Teacher(models.Model):
    short_name = models.CharField(max_length=5)
    last_name = models.CharField(max_length=50)

    def __str__(self):
        return f"Teacher {self.last_name} ({self.short_name})"


class Plan(models.Model):
    cls = models.CharField(max_length=5)
    day = models.ForeignKey(Day, related_name="plans", on_delete=models.CASCADE)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Plan for {self.cls} on {self.datetime_updated}"


class Period(models.Model):
    plan = models.ForeignKey(Plan, related_name="periods", on_delete=models.CASCADE)
    number = models.DecimalField(decimal_places=0, max_digits=2)  # 45 minute period order, e.g. 1 => 8:10-8:55
    subject = models.CharField(max_length=10)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    room = models.CharField(max_length=5)
    is_substituted = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    is_room_changed = models.BooleanField(default=False)
    is_subject_changed = models.BooleanField(default=False)

    def __eq__(self, other):
        return \
            self.number == other.number and \
            self.subject == other.subject and \
            self.room == other.room and \
            self.teacher == other.teacher
