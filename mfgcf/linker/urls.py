from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$',views.index,name = 'index'),
	url(r'^show_links/(?P<analysis_id>\w+)/(?P<metabanalysis_id>\w+)$', views.show_links,name='show_links'),
	# url(r'^get_graph/(?P<analysis_id>\w+)/(?P<metabanalysis_id>\w+)/(?P<families>\w+)$', views.get_graph,name='get_graph'),
	url(r'^get_graph/(?P<analysis_id>\w+)/(?P<metabanalysis_id>\w+)/(?P<families>\w+)/(?P<link_threshold>\d+(?:\.\d+))$', views.get_graph,name='get_graph'),
	url(r'^get_gcf_strains/(?P<gcf_id>\w+)$',views.get_gcf_strains,name = 'get_gcf_strains'),
	url(r'^get_mf_strains/(?P<mf_id>\w+)$',views.get_mf_strains,name = 'get_mf_strains'),
	url(r'^get_overlap_strains/(?P<gcf_id>\w+)/(?P<mf_id>\w+)$',views.get_overlap_strains,name = 'get_overlap_strains'),
	url(r'^showgcf/(?P<gcf_id>\w+)$',views.showgcf,name = 'showgcf'),
	url(r'^showmf/(?P<mf_id>\w+)$',views.showmf,name = 'showmf'),
	url(r'^analysis/(?P<analysis_id>\w+)$',views.show_analysis,name = 'show_analysis'),
	url(r'^metabanalysis/(?P<metabanalysis_id>\w+)$',views.show_metabanalysis,name = 'show_metabanalysis'),
	url(r'^spectra/(?P<metabanalysis_id>\w+)$',views.show_spectra,name = 'show_spectra'),
	url(r'^allmf/(?P<metabanalysis_id>\w+)$',views.show_allmf,name = 'show_allmf'),	
	url(r'^mibig$',views.show_mibig,name = 'show_mibig'),
	url(r'^validate_from_gcf/(?P<link_id>\w+)$',views.validate_from_gcf,name = 'validate_from_gcf'),
	url(r'^validate_from_mf/(?P<link_id>\w+)$',views.validate_from_mf,name = 'validate_from_mf'),
	url(r'^mibig/(?P<mibig_id>\w+)$',views.show_mibig_bgc,name = 'show_mibig_bgc'),
	url(r'^vlinks$',views.show_validated,name = 'show_validated'),
]

