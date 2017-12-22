from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Action(models.Model):
    user = models.ForeignKey(User, related_name='actions', db_index=True)
    # określa akcję podjętą przez użytkownika
    verb = models.CharField(max_length=255)
    # Kolumna typu ForeignKey prowadząca do modelu ContentType.
    # pozwala podwiązać dany obiekt action do każdego innego obiektu w projekcie
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, related_name='target_obj')

    # przechowywanie klucza podstawowego powiązanego obiektu.
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    # nie ma kolumny dla target, ale podczas pobierania powiązań to właśnie do tego
    # pola następuje odwołanie.
    # jest to relcja wiele do jendego - wiele akcj do jednego użytkownika, albo
    # wogle wiele akcji do wielu użytkowników.
    target = GenericForeignKey('target_ct', 'target_id')

    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)