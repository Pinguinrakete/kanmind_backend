from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBoardMemberOrOwner(BasePermission):
    """
    Der Benutzer muss Mitglied des Boards oder der Eigentümer sein,
    um Lesezugriff zu haben. Schreibzugriff nur für den Eigentümer.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user == obj.owner or request.user in obj.members.all()
        
        return request.user == obj.owner