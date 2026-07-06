from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Landing page
    path('', TemplateView.as_view(template_name='landing.html'), name='core_landing'),
    
    # Toolkit modules
    path('', include('accounts.urls')),
    path('', include('converter.urls')),
    
    # REST API Gateway
    path('api/', include('api.urls')),
]

# Support media streaming in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
