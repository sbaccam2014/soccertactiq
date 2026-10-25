from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PlayerProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_player_profile(sender, instance, created, **kwargs):
    """
    Every User gets exactly one PlayerProfile automatically — whether
    created via allauth signup, `createsuperuser`, or the admin "Add
    user" form. Keeps the two models in lockstep without the signup flow
    needing to know about PlayerProfile explicitly.
    """
    if created:
        PlayerProfile.objects.get_or_create(user=instance)
