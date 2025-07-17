from rest_framework import serializers
from django.contrib.auth.models import User
from kanban_app.models import Boards, Tasks, Comments


class UserInfoSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    

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


class BoardPatchSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False, write_only=True)
    owner_data = UserInfoSerializer(source='owner', read_only=True)
    members_data = UserInfoSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Boards
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']
        read_only_fields = ['id', 'owner_data', 'members_data']

    def update(self, instance, validated_data):
        members = validated_data.pop('members', None)
        if members is not None:
            instance.members.set(members)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


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
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 'assignee', 'assignee_id', 'reviewer', 'reviewer_id', 'due_date']

    def create(self, validated_data):
        validated_data['createdBy'] = self.context['request'].user
        return super().create(validated_data)


class TaskBoardSerializer(serializers.ModelSerializer):
    assignee = UserInfoSerializer(read_only=True)
    reviewer = UserInfoSerializer(read_only=True)
    
    class Meta:
        model = Tasks
        fields = ['id', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']
  

class BoardSingleSerializer(serializers.ModelSerializer):
    members = UserInfoSerializer(many=True, read_only=True)
    tasks = TaskBoardSerializer(many=True, read_only=True)

    class Meta:
        model = Boards
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
        read_only_fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        name = f"{obj.author.first_name} {obj.author.last_name}".strip()
        return name or obj.author.username