import datetime
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Action
from actions.models import Action
import web_pdb

# Zostało utworzone, aby fajnie odizolować implementację od kodu widoku
def create_action(user, verb, target=None):
    # Sprawdzenie pod kątem podobnej akcji przeprowadzonej w ciągu ostatniej minuty.
    # aby nie dodawać obiektów związanych z kliknięciem oraz odkliknięiem czegoś.
    # Jeżeli w ciągu ostatniej minuty nie była przeprowadzona identyczna akcja,
    # tworzymy nowy obiekt Action. Jeżeli został utworzony obiekt Action,
    # wartością zwrotną metody jest True, w przeciwnym razie False.
    # web_pdb.set_trace()
    now = timezone.now()
    last_minute = now - datetime.timedelta(seconds=60)
    similar_actions = Action.objects.filter(
        user_id=user.id,
        verb= verb,
        created__gte=last_minute)
    if target:
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = similar_actions.filter(target_ct=target_ct, target_id=target.id)
        # is there is no similar_actions
        if not similar_actions:
            # Nie znaleziono żadnych akcji, podobnych do podanej
            action = Action(user=user, verb=verb, target=target)
            action.save()
            return True
        return False