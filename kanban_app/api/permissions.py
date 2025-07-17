from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBoardMemberOrOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user == obj.owner or request.user in obj.members.all()
        return request.user == obj.owner
    

class IsMemberOfTasksBoard(BasePermission):

    def has_object_permission(self, request, view, obj):
        board = obj.board
        return (
            request.user == board.owner or
            request.user in board.members.all()
        )
    
    
class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user