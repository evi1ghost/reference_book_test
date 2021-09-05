from django.shortcuts import get_object_or_404
from rest_framework import permissions

from .models import Organization, Employee


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerOrModifier(permissions.BasePermission):
    def has_permission(self, request, view):
        employee = get_object_or_404(
            Employee, id=view.kwargs.get('emp_id')
        )
        return (
            request.user == employee.organization.owner
            or request.user in employee.organization.modifiers.all()
        )


class IsOwnerOrModifierOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        org = get_object_or_404(
            Organization, id=view.kwargs.get('org_id')
        )
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == org.owner
            or request.user in org.modifiers.all()
        )

    def has_object_permission(self, request, view, obj):
        org = get_object_or_404(
            Organization, id=view.kwargs.get('org_id')
        )
        return (
            request.user == org.owner
            or request.user in org.modifiers.all()
        )
