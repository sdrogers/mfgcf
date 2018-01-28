from django.conf.urls import url,include
from django.contrib import admin
from django.contrib.auth import views as auth_views
import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^people/', views.people, name='people'),
    url(r'^user_guide/', views.user_guide, name='user_guide'),
    url(r'^linker/',include('linker.urls')),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^admin/', admin.site.urls),
]
