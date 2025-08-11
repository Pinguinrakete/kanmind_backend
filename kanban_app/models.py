from django.db import models
from django.contrib.auth.models import User

"""
Model representing a project board.

Fields:
- title (CharField): The name/title of the board.
- members (ManyToManyField): Users who are members of the board.
- member_count (PositiveSmallIntegerField): Cached count of members (default 0).
- ticket_count (PositiveSmallIntegerField): Cached count of tickets/tasks on the board (default 0).
- tasks_to_do_count (PositiveSmallIntegerField): Cached count of tasks with "to do" status (default 0).
- tasks_high_prio_count (PositiveSmallIntegerField): Cached count of high priority tasks (default 0).
- owner (ForeignKey): The user who owns the board; deleting the owner deletes the board (nullable).

Methods:
- save(): On creating a new board, updates member_count to reflect current members.
- __str__(): Returns the board's title as its string representation.
"""
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

"""
Model representing a task within a board.

Fields:
- board (ForeignKey): The board this task belongs to; deleting the board deletes its tasks.
- title (CharField): Title of the task.
- description (TextField): Optional detailed description of the task.
- status (CharField): Current status of the task (default: 'to-do').
- priority (CharField): Priority level of the task (default: 'medium').
- assignee (ForeignKey): User assigned to complete the task; nullable, set to null if user deleted.
- reviewer (ForeignKey): User responsible for reviewing the task; nullable, set to null if user deleted.
- due_date (DateField): Optional deadline for the task.
- comments_count (PositiveSmallIntegerField): Cached count of comments on the task (default 0).
- createdBy (ForeignKey): User who created the task; deleting the user deletes the task.

Methods:
- __str__(): Returns the task's title as its string representation.
"""
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
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')

    def __str__(self):
        return self.title
    
"""
Model representing a comment made on a task.

Fields:
- task (ForeignKey): The task this comment belongs to; deleting the task deletes its comments.
- author (ForeignKey): The user who authored the comment; deleting the user deletes their comments.
- content (TextField): The content/text of the comment.
- created_at (DateTimeField): Timestamp when the comment was created, automatically set on creation.

Methods:
- __str__(): Returns a string indicating the author and task the comment is related to.
"""
class Comments(models.Model):
    task = models.ForeignKey('Tasks', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"