from rest_framework.permissions import BasePermission


class HasPlan(BasePermission):
    message = 'You need to be subscribed to a plan to use this API'

    def has_permission(self, request, view):
        # check if user has subscribed to a plan
        user = request.user
        if hasattr(user, 'userplan'):
            return True
        else:
            return False


class HasExpiringLinkPermissions(HasPlan):
    message = 'You do not have access to this API'

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            user_plan = request.user.userplan
            if user_plan.plan.expiring_link:
                return True
            else:
                return False
