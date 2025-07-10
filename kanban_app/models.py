from django.db import models
from django.contrib.auth.models import User

class Boards(models.Model):
    title = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='boards')
    member_count = models.PositiveSmallIntegerField(default=0)
    ticket_count = models.PositiveSmallIntegerField(default=0)
    tasks_to_do_count = models.PositiveSmallIntegerField(default=0)
    tasks_high_prio_count = models.PositiveSmallIntegerField(default=0)
    owner = models.ForeignKey(User, related_name='owned_boards', on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.member_count = self.members.count()
            super().save(update_fields=['member_count'])

    def __str__(self):
        return self.title

  
class Tasks(models.Model):
    board = models.ForeignKey(Boards, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10,default='to-do')
    priority = models.CharField(max_length=10,default='medium')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reviewed_tasks')
    due_date = models.DateField(null=True, blank=True)
    comments_count = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.title