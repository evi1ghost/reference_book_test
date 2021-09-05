from django.urls import include, path, re_path
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import (
    OrganizationCRUDViewSet,
    OrganizationListViewSet,
    EmployeeViewSet,
    PhoneCRUDViewSet,
    CreateUserViewSet,
    UserInfoViewSet,
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
router_1.register(
    'users',
    CreateUserViewSet,
    basename='user-create'
)
router_1.register(
    'users',
    UserInfoViewSet,
    basename='user-info'
)


schema_view = get_schema_view(
   openapi.Info(
      title='Reference book API',
      default_version='v1',
      description='Тестовое задание для участия в проекте "Любимовка"',
      terms_of_service='https://www.google.com/policies/terms/',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


swagger_urlpatterns = [
   re_path(
       r'^swagger(?P<format>\.json|\.yaml)$',
       schema_view.without_ui(cache_timeout=0),
       name='schema-json'
    ),
   re_path(
       r'^swagger/$',
       schema_view.with_ui('swagger', cache_timeout=0),
       name='schema-swagger-ui'
    ),
   re_path(
       r'^redoc/$',
       schema_view.with_ui('redoc', cache_timeout=0),
       name='schema-redoc'
    ),
]


auth_urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns = [
    path('v1/auth/', include(auth_urlpatterns)),
    path('v1/', include(router_1.urls)),
    path('v1/', include(swagger_urlpatterns))
]
