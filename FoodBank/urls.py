from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('restaurants.urls')),
    path('auth/', include('authentication.urls')),

]

handler404 = "helpers.views.handle_not_found"
handler500 = "helpers.views.handle_server_error"


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
