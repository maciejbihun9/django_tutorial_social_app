from django import forms
from .models import Image
from urllib import request
from django.core.files.base import ContentFile
from django.utils.text import slugify
import unicodedata
import web_pdb

class ImageCreateForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ('title', 'url', 'description')
        widgets = {'url': forms.HiddenInput,}

    # sprawdzanie poprawności podanego adresu url.
    def clean_url(self):
        url = self.cleaned_data['url']
        url_bytes = unicodedata.normalize('NFD', url).encode('ascii', 'ignore')
        url = url_bytes.decode()
        valid_extensions = ['jpg', 'jpeg', 'png']
        extension = url.rsplit('.', 1)[1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError('Podany adres URL nie zawiera '
                                        'obrazów w obsługiwanym formacie.')
        return url

    def save(self, force_insert=False,
             force_update=False,
             commit=True):

        # tak wygląda tworzenie reprezentacji obiektu na podstawie pliku models.
        image = super(ImageCreateForm, self).save(commit=False)
        image_url = self.cleaned_data['url']
        image_url_bytes = unicodedata.normalize('NFD', image_url).encode('ascii', 'ignore')
        image_url = image_url_bytes.decode()
        image_name = '{}.{}'.format(slugify(image.title),
                                    image_url.rsplit('.', 1)[1].lower())
        # Pobranie pliku obrazu z podanego adresu URL.
        response = request.urlopen(image_url)
        image.image.save(image_name,
                         ContentFile(response.read()),
                         save=False)
        if commit:
            image.save()
        return image