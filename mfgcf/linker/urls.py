from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$',views.index,name = 'index'),
	url(r'^example_graph/$', views.example_graph,name='example_graph')
]

