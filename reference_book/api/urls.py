from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    OrganizationCRUDViewSet,
    OrganizationListViewSet,
    EmployeeViewSet,
    PhoneCRUDViewSet
)


router_1 = DefaultRouter()

router_1.register(
    'organizations',
    OrganizationListViewSet,
    basename='organizations'
)
router_1.register(
    'organizations',
    OrganizationCRUDViewSet,
    basename='organization-detail'
)
router_1.register(
    r'organizations/(?P<org_id>[\d]+)/employees',
    EmployeeViewSet,
    basename='employees'
)
router_1.register(
    r'organizations/(?P<org_id>[\d]+)/employees/(?P<emp_id>[\d]+)/phones',
    PhoneCRUDViewSet,
    basename='phones'
)

auth_urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns = [
    path('v1/auth/', include(auth_urlpatterns)),
    path('v1/', include(router_1.urls))
]
