from rest_framework import permissions, viewsets
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView

from .filters import CustomSearchFilter
from .models import Employee, Organization
from .serializers import (
    EmployeeSerializer,
    OrganizationListSerializer,
)
from .pagination import ResultsSetPagination
from .permitions import IsOwnerOrAllowedUserOrReadOnly


class OrganizationListViewSet(viewsets.ModelViewSet):
    """ListViewSet for Organization with /search endpoint"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationListSerializer
    pagination_class = ResultsSetPagination
    permission_classes = [
        IsOwnerOrAllowedUserOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly
    ]
    filter_backends = [CustomSearchFilter]
    search_fields = [
        'name',
        'employees__name',
        'employees__phones__phone_number'
    ]

    @action(
        methods=['get'], detail=False,
        url_path='search', url_name='search'
    )
    def search(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class EmployeesViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
