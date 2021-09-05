from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import serializers

from .models import Employee, Organization, Phone, PERSONAL


User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']


class UserInfoSerializer(serializers.ModelSerializer):
    can_modify = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
        many=True
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'can_modify']


class PhoneSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ('id', 'phone_type', 'phone_number',)
        extra_kwargs = {
            'phone_type': {'required': True}
        }

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
    phones = PhoneSerialiser(many=True)

    def validate(self, data):
        kwargs = self.context['view'].kwargs
        name = data.get('name')
        if name:
            try:
                dublicate = Employee.objects.get(
                    name=name,
                    organization_id=kwargs['org_id']
                )
                if dublicate and dublicate.id != kwargs.get('pk'):
                    raise serializers.ValidationError(
                        'Сотрудник с таким ФИО уже существует'
                    )
            except ObjectDoesNotExist:
                pass
        return super().validate(data)

    def create(self, validated_data):
        phone_data = validated_data.pop('phones')
        employee = Employee.objects.create(**validated_data)
        Phone.objects.create(employee=employee, **phone_data[0])
        return employee

    # update не успел переопределить :-(

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
