from django.contrib import admin
from .models import Event, EventType, DiscountCode, Group

admin.site.register(Event)
admin.site.register(EventType)
admin.site.register(DiscountCode)
admin.site.register(Group)
