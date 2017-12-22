from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from .models import Contact
from actions.utils import create_action
from actions.models import Action
import web_pdb

# Create your views here.
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        # jeśli forma nie posiada dobrych danych, to zostaje zwrócona
        # z danymi, które były złe.
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'],
                            password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Uwierzytelnienie zakończyło się sukcesem.')
                else:
                    return HttpResponse('Konto jest zablokowane.')
            else:
                return HttpResponse('Nieprawidłowe dane uwierzytelniające.')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

def user_logout(request):
    if request.user.is_authenticated():
        logout(request)
        return render(request, 'registration/logged_out.html')


@login_required
def dashboard(request):
    # Domyślnie wyświetlane są wszystkie akcje za wyjątkiem bieżącego uzytkownika
    actions = Action.objects.exclude(user=request.user)
    # pobranie idków wszystkich ludzi za którymi dany gościu podążą.
    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        # Jeżeli użytkownik obserwuje innych, będzie otrzymywał jedynie informacje
        # o podejmowanych przez nich akcjach.
        actions = actions.filter(user_id__in=following_ids) \
            .select_related('user', 'user__profile') \
            .prefetch_related('target')
    # pobranie tylko 10 akcji
    actions = actions[:10]
    return render(request,
        'account/dashboard.html',
        {'section': 'dashboard',
        'actions': actions})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Utworzenie nowego obiektu użytkownika, ale jeszcze nie zapisujemy go w bazie danych.
            new_user = user_form.save(commit=False)
            # Ustawienie wybranego hasła, gdzie hasło jest odrazu zaszyfrowane.
            new_user.set_password(user_form.cleaned_data['password'])
            # Zapisanie obiektu User.
            new_user.save()
            # Utworzenie profilu użytkownika.
            profile = Profile.objects.create(user=new_user)
            create_action(new_user, 'utworzył konto', profile)
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})

@login_required
def edit(request):
    if request.method == 'POST':
        # pobranie do formy danych użytkownika wysyłającego żądanie
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Uaktualnienie profilu zakończyło się sukcesem.')
        else:
            messages.error(request, 'Wystąpił błąd podczas uaktualniania profilu.')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request,
    'account/edit.html',
    {'user_form': user_form,
    'profile_form': profile_form})

# widoki do obsługi profilu użytkownika
@login_required
def user_list(request):
    # pobranie użytkowników
    users = User.objects.filter(is_active=True)
    return render(request,
    'account/user/list.html',
    {'section': 'people',
    'users': users})

@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'account/user/detail.html', {'section': 'people', 'user': user})

@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                # śledź
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, 'obserwuje', user)
            else:
                # rezygnuj ze śledzenia
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'ok'})


