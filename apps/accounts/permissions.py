from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsAgent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'AGENT'


class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'CLIENT'


class IsAdminOrAgent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'AGENT']


class IsOwnerAdminOrAssignedAgent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'ADMIN':
            return True
        if hasattr(obj, 'client') and getattr(obj.client, 'user_id', None) == user.id:
            return True
        if hasattr(obj, 'loan') and getattr(obj.loan.client, 'user_id', None) == user.id:
            return True
        if user.role == 'AGENT':
            if hasattr(obj, 'agent') and getattr(obj.agent, 'user_id', None) == user.id:
                return True
            if hasattr(obj, 'loan') and getattr(obj.loan.agent, 'user_id', None) == user.id:
                return True
        return False


class IsAuditeur(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'AUDITEUR'


class IsComptable(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'COMPTABLE'


class IsAdminOrComptable(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'COMPTABLE']


class IsAdminOrAuditeur(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'AUDITEUR']


class IsConversationParticipant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            user.role == 'ADMIN'
            or obj.client_id == user.id
            or obj.agent_id == user.id
        )
