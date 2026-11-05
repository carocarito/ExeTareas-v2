from datetime import date
from django.conf import settings
from django.db import models

class Task(models.Model):
    class Category(models.TextChoices):
        GENERAL = "general", "General"
        IDEA = "idea", "Idea"
        FOOD = "food", "Comida"
        WORK = "work", "Trabajo"
        SPORT = "sport", "Deporte"
        MUSIC = "music", "Música"

    title = models.CharField("nombre", max_length=160)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True)
    description = models.TextField("descripción", blank=True)
    category = models.CharField(max_length=12, choices=Category.choices, default=Category.GENERAL)
    start_date = models.DateField("fecha de inicio", default=date.today)
    end_date = models.DateField("fecha de término", null=True, blank=True)
    weekdays = models.CharField(max_length=20, blank=True, help_text="0=lunes, 6=domingo")
    interval_days = models.PositiveIntegerField(default=0)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_time", "title"]

    def is_due_on(self, target):
        if not self.active or target < self.start_date or (self.end_date and target > self.end_date):
            return False
        weekly = str(target.weekday()) in self.weekdays.split(",")
        interval = self.interval_days and (target - self.start_date).days % self.interval_days == 0
        return weekly or interval

class Completion(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="completions")
    day = models.DateField()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["task", "day"], name="unique_completion_per_day")]

class PomodoroSession(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pomodoros")
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name="pomodoros")
    title = models.CharField(max_length=160, blank=True)
    work_minutes = models.PositiveSmallIntegerField(default=25)
    break_minutes = models.PositiveSmallIntegerField(default=5)
    cycles = models.PositiveSmallIntegerField(default=4)
    completed_cycles = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
