from django import forms

GCF_TYPES = ['allRiPPs','allPKSother','allOthers','allNRPS','allPKSI','allPKS-NRP','allSaccharides','allTerpene']

class GraphForm(forms.Form):
	families = forms.MultipleChoiceField(required = True,choices = zip(GCF_TYPES,GCF_TYPES),initial = ['allPKSI'])