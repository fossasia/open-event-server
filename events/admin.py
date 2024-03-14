from django.contrib import admin
from .models import Event, EventType, DiscountCode, Group, Sessions, Microlocations, SessionTypes, Tracks

admin.site.register(Event)
admin.site.register(EventType)
admin.site.register(DiscountCode)
admin.site.register(Group)
admin.site.register(Sessions)
admin.site.register(Microlocations)
admin.site.register(SessionTypes)
admin.site.register(Tracks)