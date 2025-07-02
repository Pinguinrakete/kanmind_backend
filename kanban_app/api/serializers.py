from rest_framework import serializers
from kanban_app.models import Boards

class BoardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boards
        fields = ['id','title','member_count','ticket_count','tasks_to_do_count','tasks_high_prio_count','owner_id']