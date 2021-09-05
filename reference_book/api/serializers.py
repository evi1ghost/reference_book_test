from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import permissions, serializers

from .models import Employee, Organization, Phone


User = get_user_model()


class PhoneSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ('id', 'phone_type', 'phone_number',)


class EmployeeSerializer(serializers.ModelSerializer):
    phones = PhoneSerialiser(many=True)

    class Meta:
        model = Employee
        fields = ('id', 'name', 'position', 'phones')


class OrganizationListSerializer(serializers.ModelSerializer):

    employees = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        """Dynamic fields definition"""
        super(OrganizationListSerializer, self).__init__(*args, **kwargs)

        search = self.context['request'].query_params.get('q')
        if not search:
            self.fields.pop('employees')

    def get_employees(self, obj):
        search = self.context['request'].query_params.get('q')
        employees = obj.employees.filter(
            Q(name__icontains=search)
            | Q(phones__phone_number__icontains=search)
        )[:5]
        return EmployeeSerializer(employees, many=True).data

    class Meta:
        model = Organization
        fields = ('id', 'name', 'description', 'employees',)


class OrganizationCRUDSerializer(serializers.ModelSerializer):
    modifiers = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='email',
        many=True
    )

    class Meta:
        model = Organization
        fields = ('id', 'name', 'description', 'modifiers',)


class OrganizationDetailSerializer(serializers.ModelSerializer):
    employees = EmployeeSerializer(many=True)

    class Meta:
        model = Organization
        fields = ('id', 'name', 'description', 'modifiers', 'employees')
