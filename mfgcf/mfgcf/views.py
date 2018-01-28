from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


def home(request):
    context_dict = {}
    return render(request,'mfgcf/index.html',context_dict)


def people(request):
    context_dict = {}
    return render(request,'mfgcf/people.html',context_dict)


def user_guide(request):
    markdown_str = render_to_string('markdowns/user_guide.md')
    return render(request, 'markdowns/user_guide.html', {'markdown_str':markdown_str})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})