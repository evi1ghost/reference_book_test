from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import CustomSearchFilter
from .models import Employee, Organization
from .serializers import (
    EmployeeSerializer,
    OrganizationCRUDSerializer,
    OrganizationListSerializer,
    PhoneSerialiser,
)
from .pagination import ResultsSetPagination
from .permissions import (
    IsOwnerOrModifierOrReadOnly,
    IsOwnerOrModifier,
    IsOwner
)


class OrganizationListViewSet(viewsets.GenericViewSet,
                              mixins.ListModelMixin):
    """ListViewSet for Organization with /search endpoint"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationListSerializer
    pagination_class = ResultsSetPagination
    permission_classes = [permissions.AllowAny]
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


class OrganizationCRUDViewSet(viewsets.GenericViewSet,
                              mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin):
    queryset = Organization.objects.all()
    serializer_class = OrganizationCRUDSerializer
    permission_classes = [
        IsOwner,
        permissions.IsAuthenticated
    ]

    @action(
        methods=['post'], detail=False,
        url_path='new', url_name='new',
        permission_classes=[permissions.IsAuthenticated]
    )
    def new(self, request, *args, **kwargs):
        serializer = OrganizationCRUDSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsOwnerOrModifierOrReadOnly]
    pagination_class = ResultsSetPagination
    filter_backends = [CustomSearchFilter]
    search_fields = [
        'name',
        'position',
        'phones__phone_number'
    ]

    def get_queryset(self):
        organization = get_object_or_404(
            Organization.objects.prefetch_related('employees'),
            id=self.kwargs['org_id']
        )
        return organization.employees.all()

    def perform_create(self, serializer):
        organization = get_object_or_404(
            Organization, id=self.kwargs['org_id']
        )
        serializer.save(organization=organization)


class PhoneCRUDViewSet(viewsets.ModelViewSet):
    serializer_class = PhoneSerialiser
    permission_classes = [IsOwnerOrModifier]

    def get_queryset(self):
        employee = get_object_or_404(
            Employee.objects.prefetch_related('phones'),
            id=self.kwargs['emp_id'], organization_id=self.kwargs['org_id']
        )
        return employee.phones.all()

    def perform_create(self, serializer):
        employee = get_object_or_404(
            Employee.objects.prefetch_related('phones'),
            id=self.kwargs['emp_id'], organization_id=self.kwargs['org_id']
        )
        serializer.save(employee=employee)
