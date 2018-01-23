from django import forms

GCF_TYPES = ['allRiPPs','allPKSother','allOthers','allNRPS','allPKSI','allPKS-NRP','allSaccharides','allTerpene']

class GraphForm(forms.Form):
	families = forms.MultipleChoiceField(required = True,choices = zip(GCF_TYPES,GCF_TYPES),initial = ['allPKSI'])
	link_threshold = forms.FloatField(required = True, initial = 0.01)

class AnnotationForm(forms.Form):
	annotation = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 100}))