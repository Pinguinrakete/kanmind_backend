from rest_framework import serializers
from django.contrib.auth.models import User
from kanban_app.models import Boards, Tasks, Comments

"""
This serializer returns user data.

Returns: user ID, email address, and full name (combined from first and last name).
Note: The email field is read-only.
"""
class UserInfoSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
"""
This serializer handles board creation.

Method: POST  
Accepts:  
- title (string)  
- members (list of user IDs, optional)

Returns:  
- board ID  
- title  
- member count  
- ticket count  
- tasks to do count  
- high priority tasks count  
- owner ID

Note:  
- The 'members' field is write-only and optional.  
- All returned fields except 'title' are read-only.
- The requesting user is automatically set as the owner and added as a member.
"""
class BoardSerializer(serializers.ModelSerializer):
    members = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Boards
        fields = ['id', 'title', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id', 'members']
        read_only_fields = ['id', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']

    def create(self, validated_data):
        members = validated_data.pop('members', [])
        user = self.context['request'].user

        board = Boards.objects.create(owner=user, **validated_data)
        board.members.set(User.objects.filter(id__in=members + [user.id]))
        board.member_count = board.members.count()
        board.save()

        return board

"""
This serializer handles board updates (partial or full).

Method: PATCH or PUT  
Accepts:  
- title (string, optional)  
- members (list of user IDs, optional)

Returns:  
- board ID  
- updated title  
- owner data (read-only, includes ID, email, and full name)  
- member data (read-only, includes IDs, emails, and full names)

Notes:  
- The 'members' field is write-only.  
- 'owner_data' and 'members_data' are read-only and returned in the response.  
- If 'members' are provided, the current board members will be replaced with the given list.
"""
class BoardPatchSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False, write_only=True)
    owner_data = UserInfoSerializer(source='owner', read_only=True)
    members_data = UserInfoSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Boards
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']
        read_only_fields = ['id', 'owner_data', 'members_data']

    def validate_members(self, value):
        user_ids = [user.id for user in value]
        existing_ids = set(User.objects.filter(id__in=user_ids).values_list('id', flat=True))
        if len(existing_ids) != len(user_ids):
            raise serializers.ValidationError("Invalid request data. Some users may be invalid.")
        return value

    def update(self, instance, validated_data):
        members = validated_data.pop('members', None)
        if members is not None:
            instance.members.set(members)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

"""
This serializer handles task creation or update with assignee and reviewer information.

Method: POST / PATCH / PUT  
Accepts:  
- board (ID of the board the task belongs to)  
- title (string)  
- description (string)  
- status (string)  
- priority (string/int)  
- assignee_id (user ID)  
- reviewer_id (user ID)  
- due_date (datetime)

Returns:  
- task ID  
- board ID  
- title  
- description  
- status  
- priority  
- assignee (user info: ID, email, full name)  
- reviewer (user info: ID, email, full name)  
- due_date  
- comments_count (number of comments on the task)

Notes:  
- 'assignee_id' and 'reviewer_id' are write-only; use them to assign users.  
- 'assignee' and 'reviewer' are read-only and provide user info.  
- This serializer supports both creating and updating tasks.
"""
class TaskReviewingAndAssignedToMeSerializer(serializers.ModelSerializer):
    assignee = UserInfoSerializer(read_only=True)
    reviewer = UserInfoSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', write_only=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer', write_only=True
    )
    
    class Meta:
        model = Tasks
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 'assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'due_date','comments_count']

"""
This serializer handles task creation.

Method: POST  
Accepts:  
- board (ID of the board the task belongs to)  
- title (string)  
- description (string)  
- status (string)  
- priority (string/int)  
- assignee_id (user ID)  
- reviewer_id (user ID)  
- due_date (datetime)

Returns:  
- task ID  
- board ID  
- title  
- description  
- status  
- priority  
- assignee (user info: ID, email, full name)  
- reviewer (user info: ID, email, full name)  
- due_date

Notes:  
- 'assignee_id' and 'reviewer_id' are write-only.  
- 'assignee' and 'reviewer' are read-only user info objects.  
- The user making the request is automatically set as the task creator (`createdBy`).
"""
class TaskSerializer(serializers.ModelSerializer):
    assignee = UserInfoSerializer(read_only=True)
    reviewer = UserInfoSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', write_only=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer', write_only=True
    )
    
    class Meta:
        model = Tasks
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 'assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'comments_count', 'due_date']

    def create(self, validated_data):
        validated_data['createdBy'] = self.context['request'].user
        return super().create(validated_data)

"""
This serializer returns task data for display within a board.

Method: GET  
Returns:  
- task ID  
- title (string)  
- description (string)  
- status (string)  
- priority (string/int)  
- assignee (user info: ID, email, full name)  
- reviewer (user info: ID, email, full name)  
- due_date (datetime)  
- comments_count (number of comments on the task)

Notes:  
- This serializer is read-only.  
- Used to list or retrieve tasks within the context of a board.  
- 'assignee' and 'reviewer' are nested user objects.
"""
class TaskBoardSerializer(serializers.ModelSerializer):
    assignee = UserInfoSerializer(read_only=True)
    reviewer = UserInfoSerializer(read_only=True)
    
    class Meta:
        model = Tasks
        fields = ['id', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']

"""  
This serializer returns detailed information for a single board.

Method: GET  
Returns:  
- board ID  
- title (string)  
- owner ID (user ID of the board owner)  
- members (list of user info objects: ID, email, full name)  
- tasks (list of task objects, including title, status, assignee, reviewer, etc.)

Notes:  
- All fields are read-only.  
- Used to retrieve full board details, including members and associated tasks.
"""
class BoardSingleSerializer(serializers.ModelSerializer):
    members = UserInfoSerializer(many=True, read_only=True)
    tasks = TaskBoardSerializer(many=True, read_only=True)

    class Meta:
        model = Boards
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
        read_only_fields = ['id', 'title', 'owner_id', 'members', 'tasks']

"""
This serializer handles comment creation and returns comment data.

Method: POST / GET  
Accepts (on POST):  
- content (string)

Returns:  
- comment ID  
- created_at (timestamp)  
- author (string: full name or username)  
- content (string)

Notes:  
- 'author' is a read-only string derived from the comment author's full name or username.  
- 'id', 'created_at', and 'author' are read-only.  
- Used to post new comments or retrieve existing ones on tasks.
"""
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comments
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        name = f"{obj.author.first_name} {obj.author.last_name}".strip()
        return name or obj.author.username
    
    def create(self, validated_data):
        comment = Comments.objects.create(**validated_data)

        task = comment.task
        task.comments_count = task.comments.count()
        task.save(update_fields=['comments_count'])

        return comment