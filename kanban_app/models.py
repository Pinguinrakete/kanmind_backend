from django.db import models
from django.contrib.auth.models import User

class Boards(models.Model):
    title = models.CharField(max_length=255)
    owner_id = models.ForeignKey(User, related_name='owned_boards', on_delete=models.CASCADE,null=True)
    members = models.ManyToManyField(User, related_name='boards')
    member_count = models.PositiveSmallIntegerField(default=0)
    ticket_count = models.PositiveSmallIntegerField(default=0)
    tasks_to_do_count = models.PositiveSmallIntegerField(default=0)
    tasks_high_prio_count = models.PositiveSmallIntegerField(default=0)

    def save(self, *args, **kwargs):
        # Optionale automatische Aktualisierung der member_count
        self.member_count = self.members.count()
        super().save(*args, **kwargs)

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



# class Tasks(models.Model):
#     board = models.PositiveSmallIntegerField(default=0)
#     title = models.CharField(max_length=255)
#     description = models.CharField(max_length=255)
#     status = models.CharField(max_length=15)
#     priority = models.CharField(max_length=10)
#     assignee = {
#         "id": models.PositiveSmallIntegerField(default=0),
#         "email": models.CharField(max_length=255),
#         "fullname": models.CharField(max_length=255)
#     },        
#     reviewer_id = {
#         "id": models.PositiveSmallIntegerField(default=0),
#         "email": models.CharField(max_length=255),
#         "fullname": models.CharField(max_length=255)
#     },
#     due_date = models.DateField()
    
#     def __str__(self):
#         return self.title

#         "id": null,
#         "title": null,
#         "description": null,
#         "status": null,
#         "priority": 'medium',
#         "assignee": null,
#         "reviewer": null,
#         "due_date": null