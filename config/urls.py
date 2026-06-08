from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.support_chat.views_chat_template import chat_page

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', chat_page, name='chat-page'),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/loans/', include('apps.loans.urls')),
    path('api/repayments/', include('apps.repayments.urls')),
    path('api/insurance/', include('apps.insurance.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/chat/', include('apps.support_chat.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
