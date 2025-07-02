from django.db import models
from django.contrib.auth.models import User

class Boards(models.Model):
    title = models.CharField(max_length=255)
    member_count = models.PositiveSmallIntegerField(default=0)
    ticket_count = models.PositiveSmallIntegerField(default=0)
    tasks_to_do_count = models.PositiveSmallIntegerField(default=0)
    tasks_high_prio_count = models.PositiveSmallIntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title