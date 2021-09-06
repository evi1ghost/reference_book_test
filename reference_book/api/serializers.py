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
        """
        Check if phone from data already used as personal and prevent from
        using work number as a personal
        """
        existing_phone = None
        existing_phone_pk = self.context['view'].kwargs.get('pk')
        if existing_phone_pk:
            try:
                existing_phone = Phone.objects.get(pk=existing_phone_pk)
            except ObjectDoesNotExist:
                pass
        new_number = (
            data.get('phone_number') or existing_phone.phone_number
        )
        dublicate = Phone.objects.filter(phone_number=new_number)
        if (
            # добавляемый номер не существует:
            not dublicate
            # номер встречается более 1 раза, значит не персональный -
            # можем создать такой же неперсональный номер:
            or len(dublicate) > 1 and data.get('phone_type') != PERSONAL
            # номер встречается 1 раз и принадлежит текущему сотруднику
            # тип запроса patch или put поскольку в url есть pk:
            or len(dublicate) == 1 and dublicate[0] == existing_phone
            # номер встречается 1 раз и он не персональный - не пытаемся
            # создать такой же персональный номер:
            or len(dublicate) == 1 and dublicate[0].phone_type != PERSONAL
            and data.get('phone_type') != PERSONAL
        ):
            return data
        raise serializers.ValidationError(
            'Данный номер искользуется в качестве личного иным'
            ' сотрудником либо вы пытаетесь сохранить рабочий номер'
            ' в качестве личного'
        )


class EmployeeSerializer(serializers.ModelSerializer):
    phones = PhoneSerialiser(many=True)

    def validate(self, data):
        """
        Check if the employee with same name exists in current organization
        """
        kwargs = self.context['view'].kwargs
        name = data.get('name')
        if name:
            try:
                dublicate = Employee.objects.get(
                    name=name,
                    organization_id=kwargs['org_id']
                )
                request_emp_id = kwargs.get('pk')
                if request_emp_id:
                    request_emp_id = int(request_emp_id)
                if dublicate and dublicate.id != request_emp_id:
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

    def update(self, instance, validated_data):
        # Phone's information can be updated through phones/ endpoint
        validated_data.pop('phones', {})
        return super().update(instance, validated_data)

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
        fields = ('id', 'name', 'address', 'description', 'employees',)


class OrganizationCRUDSerializer(serializers.ModelSerializer):
    modifiers = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='email',
        many=True,
        required=False
    )

    class Meta:
        model = Organization
        fields = ('id', 'name', 'address', 'description', 'modifiers',)
