from django.contrib import admin

from multigtfsrt.models import (TransitFeed, FeedMessage, FeedHeader, StopTimeEvent, StopTimeUpdate, TimeRange, Position,
TripDescriptor, VehicleDescriptor, EntitySelector, TranslatedString, Translation, TripUpdate, VehiclePosition, Alert)
# Register your models here.

admin.site.register(TransitFeed)
admin.site.register(FeedMessage)
admin.site.register(FeedHeader)
admin.site.register(StopTimeEvent)
admin.site.register(StopTimeUpdate)
admin.site.register(TimeRange)
admin.site.register(Position)
admin.site.register(TripDescriptor)
admin.site.register(VehicleDescriptor)
admin.site.register(EntitySelector)
admin.site.register(TranslatedString)
admin.site.register(Translation)
admin.site.register(TripUpdate)
admin.site.register(VehiclePosition)
admin.site.register(Alert)
