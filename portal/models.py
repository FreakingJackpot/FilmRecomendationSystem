from django.db import models
from django.utils.translation import gettext_lazy as _


class YoutubeChannel(models.Model):
    channel_id = models.TextField()
    ru_name = models.TextField()
    eng_name = models.TextField()
    language_type = models.TextField()

    class Meta:
        verbose_name_plural = _('Youtube сhannels')
        verbose_name = _('Youtube сhannel')

    def __str__(self):
        return self.ru_name
