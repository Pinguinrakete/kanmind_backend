from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBoardMemberOrOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user == obj.owner or request.user in obj.members.all()
        return request.user == obj.owner