from django.db import models

# Create your models here.
class TransitFeed(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    main_url = models.URLField()
    alert_url = models.URLField()
    trip_update_url = models.URLField()
    vehicle_url = models.URLField()
    update_timeout = models.IntegerField()
    
class FeedMessage(models.Model):
    transit_feed = models.ForeignKey(TransitFeed)
    header = models.ForeignKey('FeedHeader')

INCREMENTALITY = (
    (0, "FULL_DATASET"),
    (1, "DIFFERENTIAL"),
)

class FeedHeader(models.Model):
    gtfs_realtime_version = models.CharField(max_length=20)
    incrementality = models.CharField(max_length = 15, choices=INCREMENTALITY, blank=True)
    timestamp = models.BigIntegerField(blank=True)

class FeedEntity(models.Model):
    oid = models.CharField(max_length=30)
    is_deleted = models.BooleanField(blank=True)
    feed_message = models.ForeignKey(FeedMessage)

    class Meta:
        abstract = True

class TripUpdate(FeedEntity):
    trip = models.ForeignKey('TripDescriptor')
    vehicle = models.ForeignKey('VehicleDescriptor', blank=True)
    timestamp = models.BigIntegerField(blank=True)

class StopTimeEvent(models.Model):
    delay = models.BigIntegerField(blank=True)
    time = models.IntegerField(blank=True)
    uncertainty = models.BigIntegerField(blank=True)

SCHEDULE_RELATIONSHIP = (
    (0, "SCHEDULED"),
    (1, "SKIPPED"),
    (2, "NO_DATA"),
)

class StopTimeUpdate(models.Model):
    stop_sequence = models.IntegerField(blank=True)
    stop_id = models.CharField(max_length=30)
    arrival = models.ForeignKey(StopTimeEvent, blank=True, related_name='st_arrival')
    departure = models.ForeignKey(StopTimeEvent, blank=True, related_name='st_departure')
    schedule_relationship = models.CharField(max_length=15, choices = SCHEDULE_RELATIONSHIP, blank=True)
    trip_update = models.ForeignKey(TripUpdate, blank=True, related_name='st_trip_update')

VEHICLE_STOP_STATUS = (
    (0, "INCOMING_AT"),   # The vehicle is just about to arrive at the stop (on a stop display, the vehicle symbol typically flashes).
    (1, "STOPPED_AT"),    # The vehicle is standing at the stop.
    (2, "IN_TRANSIT_TO"), # The vehicle has departed the previous stop and is in transit.
)

CONGESTION_LEVEL = (
    (0, "UNKNOWN_CONGESTION_LEVEL"),
    (1, "RUNNING_SMOOTHLY"),
    (2, "STOP_AND_GO"),
    (3, "CONGESTION"),
    (4, "SEVERE_CONGESTION"),
)

class VehiclePosition(FeedEntity):
    trip = models.ForeignKey('TripDescriptor', blank=True)
    vehicle = models.ForeignKey('VehicleDescriptor', blank=True)
    position = models.ForeignKey('Position', blank = True)
    current_stop_sequence = models.IntegerField(blank=True)
    stop_id = models.CharField(max_length=30, blank=True)
    current_status = models.CharField(max_length=30, choices=VEHICLE_STOP_STATUS, blank=True)
    timestamp = models.BigIntegerField(blank=True)
    congestion_level = models.CharField(max_length=30, choices=CONGESTION_LEVEL, blank=True)

CAUSE = (
    (1, "UNKNOWN_CAUSE"),
    (2, "OTHER_CAUSE"),
    (3, "TECHNICAL_PROBLEM"),
    (4, "STRIKE"),
    (5, "DEMONSTRATION"),
    (6, "ACCIDENT"),
    (7, "HOLIDAY"),
    (8, "WEATHER"),
    (9, "MAINTENANCE"),
    (10, "CONSTRUCTION"),
    (11, "POLICE_ACTIVITY"),
    (12, "MEDICAL_EMERGENCY"),
)

EFFECT = (
    (1, "NO_SERVICE"),
    (2, "REDUCED_SERVICE"),
    (3, "SIGNIFICANT_DELAYS"),
    (4, "DETOUR"),
    (5, "ADDITIONAL_SERVICE"),
    (6, "MODIFIED_SERVICE"),
    (7, "OTHER_EFFECT"),
    (8, "UNKNOWN_EFFECT"),
    (9, "STOP_MOVED"),
)

class Alert(FeedEntity):
    cause = models.CharField(max_length=30, choices=CAUSE, blank=True)
    effect = models.CharField(max_length=30, choices=EFFECT, blank=True)
    url = models.ForeignKey('TranslatedString', blank=True, related_name='a_url')
    header_text = models.ForeignKey('TranslatedString', blank=True, related_name='a_header_text')
    description_text = models.ForeignKey('TranslatedString', blank=True, related_name='a_description_text')

class TimeRange(models.Model):
    alert = models.ForeignKey(Alert, related_name='active_period')
    start = models.BigIntegerField(blank=True)
    end = models.BigIntegerField(blank=True)

class Position(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    bearing = models.FloatField(blank=True)
    odometer = models.FloatField(blank=True)
    speed = models.FloatField(blank=True)

SCHEDULE_RELATIONSHIP = (
    (0, "SCHEDULED"),
    (1, "ADDED"),
    (2, "UNSCHEDULED"),
    (3, "CANCELED"),
    (5, "REPLACEMENT"),
)

class TripDescriptor(models.Model):
    trip_id = models.CharField(max_length=30, blank=True)
    route_id = models.CharField(max_length=30, blank=True)
    start_time = models.CharField(max_length=30, blank=True)
    start_date = models.CharField(max_length=30, blank=True)
    schedule_relationship = models.CharField(max_length=30, choices=SCHEDULE_RELATIONSHIP, blank=True)

class VehicleDescriptor(models.Model):
    oid = models.CharField(max_length=30, blank=True)
    label = models.CharField(max_length=30, blank=True)
    license_plate = models.CharField(max_length=30, blank=True)

class EntitySelector(models.Model):
    alert = models.ForeignKey(Alert, related_name='informed_entity')
    agency_id = models.CharField(max_length=30, blank=True)
    route_id = models.CharField(max_length=30, blank=True)
    route_type = models.IntegerField(blank=True)
    trip = models.ForeignKey(TripDescriptor, blank=True)
    stop_id = models.CharField(max_length=30, blank=True)

class TranslatedString(models.Model):
    pass

class Translation(models.Model):
    text = models.TextField()
    language = models.TextField(blank=True)
    translated_string = models.ForeignKey(TranslatedString)
