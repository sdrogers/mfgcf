from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$',views.index,name = 'index'),
	url(r'^show_graph/$', views.show_graph,name='show_graph'),
	url(r'^get_graph/$', views.get_graph,name='get_graph'),
	url(r'^get_gcf_strains/(?P<gcf_id>\w+)$',views.get_gcf_strains,name = 'get_gcf_strains'),
	url(r'^get_mf_strains/(?P<mf_id>\w+)$',views.get_mf_strains,name = 'get_mf_strains'),
	url(r'^get_overlap_strains/(?P<gcf_id>\w+)/(?P<mf_id>\w+)$',views.get_overlap_strains,name = 'get_overlap_strains'),
]

