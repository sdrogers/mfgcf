from django.shortcuts import render
from django.template.loader import render_to_string


def home(request):
    context_dict = {}
    return render(request,'mfgcf/index.html',context_dict)


def people(request):
    context_dict = {}
    return render(request,'mfgcf/people.html',context_dict)


def user_guide(request):
    markdown_str = render_to_string('markdowns/user_guide.md')
    return render(request, 'markdowns/user_guide.html', {'markdown_str':markdown_str})