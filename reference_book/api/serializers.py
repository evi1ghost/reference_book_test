from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import serializers

from .models import Employee, Organization, Phone, PERSONAL


User = get_user_model()


class PhoneSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ('id', 'phone_type', 'phone_number',)

    def validate(self, data):
        kwargs = self.context['view'].kwargs
        try:
            dublicate = Phone.objects.get(
                phone_number=data['phone_number'],
                phone_type=PERSONAL
            )
            if dublicate and dublicate.id != kwargs.get('pk'):
                raise serializers.ValidationError(
                    'Данный номер искользуется в качестве'
                    'личного иным сотрудником'
                )
        except ObjectDoesNotExist:
            pass
        return data


class EmployeeSerializer(serializers.ModelSerializer):
    phones = PhoneSerialiser(many=True, read_only=True)

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
