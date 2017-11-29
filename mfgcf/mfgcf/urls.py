from django.conf.urls import url,include
from django.contrib import admin
import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^people/', views.people, name='people'),
    url(r'^user_guide/', views.user_guide, name='user_guide'),
    url(r'^linker/',include('linker.urls')),
    url(r'^admin/', admin.site.urls),
]
