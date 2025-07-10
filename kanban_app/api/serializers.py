from rest_framework import serializers
from django.contrib.auth.models import User
from kanban_app.models import Boards, Tasks


class UserInfoSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

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


class BoardSingleSerializer(serializers.ModelSerializer):
    members = UserInfoSerializer(many=True, read_only=True)

    class Meta:
        model = Boards
        fields = ['id', 'title', 'owner_id', 'members']
        read_only_fields = ['id', 'title', 'owner_id', 'members']


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserInfoSerializer(read_only=True)
    reviewer = UserInfoSerializer(read_only=True)
    
    class Meta:
        model = Tasks
        fields = ['id','board', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date', 'comments_count']
   