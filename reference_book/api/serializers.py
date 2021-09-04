# from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers
# from rest_framework_simplejwt.serializers import TokenObtainSerializer
# from rest_framework_simplejwt.tokens import RefreshToken

from .models import Employee, Organization, Phone


# User = get_user_model()


# class EmailTokenObtainSerializer(TokenObtainSerializer):
#     username_field = User.EMAIL_FIELD


# class CustomTokenObtainPairSerializer(EmailTokenObtainSerializer):
#     @classmethod
#     def get_token(cls, user):
#         return RefreshToken.for_user(user)

#     def validate(self, attrs):
#         data = super().validate(attrs)

#         refresh = self.get_token(self.user)

#         data["refresh"] = str(refresh)
#         data["access"] = str(refresh.access_token)

#         return data


class PhoneSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ('id', 'phone_type', 'phone_number',)


class EmployeeSerializer(serializers.ModelSerializer):
    phones = PhoneSerialiser(many=True)

    class Meta:
        model = Employee
        fields = ('id', 'name', 'position', 'phones')


class OrganizationListSerializer(serializers.HyperlinkedModelSerializer):

    def __init__(self, *args, **kwargs):
        """Dynamic fields definition"""
        super(OrganizationListSerializer, self).__init__(*args, **kwargs)

        search = self.context['request'].query_params.get('q')
        if not search:
            self.fields.pop('employees')

    employees = serializers.SerializerMethodField()

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


class OrganizationDetailSerializer(serializers.ModelSerializer):
    employees = EmployeeSerializer(many=True)

    class Meta:
        model = Organization
        fields = ('id', 'name', 'description', 'employees')
