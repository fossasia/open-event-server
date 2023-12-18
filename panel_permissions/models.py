from django.db import models


class PanelPermission(models.Model):
    panel_name = models.CharField(null=True, blank=True, max_length=200)
    can_access = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"{self.panel_name} - {self.can_access}"
