from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from django.shortcuts import get_object_or_404
from .models import Image
from common.decorators import ajax_required
from actions.utils import create_action
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.http import JsonResponse
from django.views.decorators.http import require_POST

import redis
from django.conf import settings

import web_pdb

# Nawiązanie połączenia z bazą danych Redis.
r = redis.StrictRedis(host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB)

@login_required
def image_create(request):
    if request.method == 'POST':
        # Formularz został wysłany.
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # Dane formularza są prawidłowe.
            cd = form.cleaned_data
            # ten save() jest wywołany na formie.
            new_item = form.save(commit=False)
            # Przypisanie bieżącego użytkownika do elementu.
            new_item.user = request.user
            # a ten save na obiekcie utworzonym na podstawie tej formy,
            # czyli nadpisana metoda z fromy to nie ta, która zarządza zapisywanie tego obiektu.
            new_item.save()
            # utworzenie akcji związanej z zapisaniem obrazu
            create_action(request.user, 'dodał obraz', new_item)

            messages.success(request, 'Obraz został dodany.')
            # Przekierowanie do widoku szczegółowego dla nowo utworzonego elementu.
            return redirect(new_item.get_absolute_url())
    else:
        # Utworzenie formularza na podstawie danych dostarczonych przez bookmarklet w żądaniu GET.
        form = ImageCreateForm(data=request.GET)
    return render(request, 'images/image/create.html', {'section': 'images','form': form})

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    total_views = r.incr('image:{}:views'.format(image.id))
    # Inkrementacja o 1 rankingu danego obrazu.
    r.zincrby('image_ranking', image.id, 1)
    return render(request, 'images/image/detail.html',
                  {'section': 'images',
                   'image': image,
                   'total_views': total_views})

@login_required
@require_POST
@ajax_required
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                # web_pdb.set_trace()
                image.users_like.add(request.user)
                # akcja polubienia
                create_action(request.user, 'polubił', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status':'ok'})
        except:
            pass
    return JsonResponse({'status':'ok'})

@login_required
def image_list(request):
    # pobranie obrazór wszystkich
    images = Image.objects.all()
    # paginator dla 8 obrazów na stronę
    paginator = Paginator(images, 8)
    #
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # Jeżeli zmienna page nie jest liczbą całkowitą, wówczas pobierana jest pierwsza strona wyników.
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # Jeżeli żądanie jest w technologii AJAX i zmienna page ma wartość spoza zakresu,
            # wówczas zwracana jest pusta strona.
            return HttpResponse('')
            # Jeżeli zmienna page ma wartość większą niż numer ostatniej strony wyników, wtedy pobierana
            # jest ostatnia strona wyników.
            images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'images/image/list_ajax.html', {'section': 'images', 'images': images})
    return render(request, 'images/image/list.html', {'section': 'images', 'images': images})

@login_required
def image_ranking(request):
    # Pobranie słownika rankingu obrazów.
    n_items = r.zcard("image_ranking")
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    # Pobranie najczęściej wyświetlanych obrazów.
    # pobieranie jest wymuszone poprzez wywołanie metody list
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    # Obiekty Image są sortowane według indeksu występowania w rankingu obrazów.
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request, 'images/image/ranking.html',
                  {'section': 'images', 'most_viewed': most_viewed})