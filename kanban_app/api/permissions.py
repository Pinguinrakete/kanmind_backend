from rest_framework.permissions import BasePermission, SAFE_METHODS

"""
Custom permission: Allows access to board members or the board owner.

Rules:
- **Read access (GET, HEAD, OPTIONS):**
  - Allowed if the user is the board owner or a member of the board.
- **Write access (PATCH, DELETE, etc.):**
  - Allowed **only** if the user is the board owner.

Used for securing board-related views, ensuring members can view but only the owner can modify.

Example usage:
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]
"""
class IsBoardMemberOrOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user == obj.owner or request.user in obj.members.all()
        return request.user == obj.owner
    
"""
Custom permission: Allows access only to members or the owner of the task's board.

Rules:
- The authenticated user must be either:
  - the owner of the board the task belongs to, or
  - a member of that board.

Used for securing task-related or comment-related views,
ensuring only those involved in the board can access or modify the task or its comments.

Example usage:
    permission_classes = [IsAuthenticated, IsMemberOfTasksBoard]
"""
class IsMemberOfTasksBoard(BasePermission):

    def has_object_permission(self, request, view, obj):
        board = obj.board
        return (
            request.user == board.owner or
            request.user in board.members.all()
        )
    
"""
Custom permission: Allows access only to the author of a comment.

Rules:
- The authenticated user must be the one who created the comment.

Typically used to ensure that only the original comment author can delete their comment.

Example usage:
    permission_classes = [IsAuthenticated, IsCommentAuthor]
""" 
class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user