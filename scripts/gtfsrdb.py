#!/usr/bin/python

# gtfsrdb.py: load gtfs-realtime data to a database

import gtfs_realtime_pb2
import time
import sys
import datetime
from urllib2 import urlopen
from multigtfsrt.models import *

# Get a specific translation from a TranslatedString
def getTrans(string, lang):
    # If we don't find the requested language, return this
    untranslated = None

    # single translation, return it
    if len(string.translation) == 1:
        return string.translation[0].text

    for t in string.translation:
        if t.language == lang:
            return t.text
        if t.language == None:
            untranslated = t.text
    return untranslated

def run():
    feed = TransitFeed.objects.all()[0] 

    while True:
        fm = gtfs_realtime_pb2.FeedMessage()
        fm.ParseFromString(
            urlopen(feed.trip_update_url).read()
        )

        # Check the feed version
        if fm.header.gtfs_realtime_version != u'1.0':
            print 'Warning: feed version has changed: found %s, expected 1.0' % fm.header.gtfs_realtime_version
        timestamp = fm.header.timestamp

        dbfh = FeedHeader(
            gtfs_realtime_version = fm.header.gtfs_realtime_version,
            incrementality = fm.header.incrementality,
            timestamp = fm.header.timestamp)
        dbfh.save()
        
        dbfm = FeedMessage(transit_feed=feed, header=dbfh)
        dbfm.save()

        print 'Adding %s trip updates' % len(fm.entity)
        for entity in fm.entity:
            tu = entity.trip_update
            dbtd = TripDescriptor(
                trip_id = tu.trip.trip_id,
                route_id = tu.trip.route_id,
                start_time = tu.trip.start_time,
                start_date = tu.trip.start_date,
                schedule_relationship = tu.trip.schedule_relationship)
            dbtd.save()
            dbvd = VehicleDescriptor(
                oid = tu.vehicle.id,
                label = tu.vehicle.label,
                license_plate = tu.vehicle.license_plate)
            dbvd.save()

            dbtu = TripUpdate(
                oid = entity.id,
                is_deleted = entity.is_deleted,
                feed_message = dbfm,
                trip = dbtd,
                vehicle = dbvd,
                timestamp = timestamp)
            dbtu.save()

            #print 'Adding %s stop time updates' % len(tu.stop_time_update)
            for stu in tu.stop_time_update:
                dbstua = StopTimeEvent(
                    delay = stu.arrival.delay,
                    time = stu.arrival.time,
                    uncertainty = stu.arrival.uncertainty)
                dbstua.save()

                dbstud = StopTimeEvent(
                    delay = stu.departure.delay,
                    time = stu.departure.time,
                    uncertainty = stu.departure.uncertainty)
                dbstud.save()
                
                dbstu = StopTimeUpdate(
                    stop_sequence = stu.stop_sequence,
                    stop_id = stu.stop_id,
                    arrival = dbstua,
                    departure = dbstud,
                    schedule_relationship = stu.schedule_relationship,
                    trip_update = dbtu)
                dbstu.save()

        fm = gtfs_realtime_pb2.FeedMessage()
        fm.ParseFromString(
            urlopen(feed.alert_url).read()
        )

        # Check the feed version
        if fm.header.gtfs_realtime_version != u'1.0':
            print 'Warning: feed version has changed: found %s, expected 1.0' % fm.header.gtfs_realtime_version
        timestamp = fm.header.timestamp

        dbfh = FeedHeader(
            gtfs_realtime_version = fm.header.gtfs_realtime_version,
            incrementality = fm.header.incrementality,
            timestamp = fm.header.timestamp)
        dbfh.save()

        dbfm = FeedMessage(transit_feed=feed, header=dbfh)
        dbfm.save()

        print 'Adding %s alerts' % len(fm.entity)
        for entity in fm.entity:
            al = entity.alert
            dburl = TranslatedString()
            dburl.save()
            dbht = TranslatedString()
            dbht.save()
            dbdt = TranslatedString()
            dbdt.save()

            dbal = Alert(
                oid = entity.id,
                is_deleted = entity.is_deleted,
                feed_message = dbfm,
                cause = al.cause,
                effect = al.effect,
                url = dburl,
                header_text = dbht,
                description_text = dbdt,
                timestamp = timestamp)
            dbal.save()

            for tr in al.active_period:
                dbtr = TimeRange(
                    alert = dbal,
                    start = tr.start,
                    end = tr.end)
                dbtr.save()

            for ie in al.informed_entity:
                dbietd = TripDescriptor(
                    trip_id = ie.trip.trip_id,
                    route_id = ie.trip.route_id,
                    start_time = ie.trip.start_time,
                    start_date = ie.trip_start_date,
                    schedule_relationship = ie.trip.schedule_relationship)
                dbietd.save()
                dbie = EntitySelector(
                    alert = dbal,
                    agency_id = ie.agency_id,
                    route_id = ie.route_id,
                    route_type = ie.route_type,
                    trip = dbietd,
                    stop_id = ie.stop_id)
                dbie.save()

            for trans in al.url.translation:
                dbtrans = Translation(
                    text = trans.text,
                    language = trans.language,
                    translated_string = dburl)
                dbtrans.save()

            for trans in al.header_text.translation:
                dbtrans = Translation(
                    text = trans.text,
                    language = trans.language,
                    translated_string = dbht)
                dbtrans.save()
            
            for trans in al.description_text.translation:
                dbtrans = Translation(
                    text = trans.text,
                    language = trans.language,
                    translated_string = dbdt)
                dbtrans.save()

        fm = gtfs_realtime_pb2.FeedMessage()
        fm.ParseFromString(
            urlopen(feed.vehicle_url).read()
        )

        # Check the feed version
        if fm.header.gtfs_realtime_version != u'1.0':
            print 'Warning: feed version has changed: found %s, expected 1.0' % fm.header.gtfs_realtime_version
        timestamp = fm.header.timestamp

        dbfh = FeedHeader(
            gtfs_realtime_version = fm.header.gtfs_realtime_version,
            incrementality = fm.header.incrementality,
            timestamp = fm.header.timestamp)
        dbfh.save()

        dbfm = FeedMessage(transit_feed=feed, header=dbfh)
        dbfm.save()

        print 'Adding %s vehicles' % len(fm.entity)
        for entity in fm.entity:
            v = entity.vehicle
            dbp = Position(
                latitude = v.position.latitude,
                longitude = v.position.longitude,
                speed = float(v.position.speed),
                odometer = float(v.position.odometer),
                bearing = float(v.position.bearing))
            dbp.save()
            dbtd = TripDescriptor(
                trip_id = v.trip.trip_id,
                start_time = v.trip.start_time,
                start_date = v.trip.start_date,
                route_id = v.trip.route_id,
                schedule_relationship = v.trip.schedule_relationship)
            dbtd.save()
            dbvd = VehicleDescriptor(
                oid = v.vehicle.id,
                label = v.vehicle.label,
                license_plate = v.vehicle.license_plate)
            dbvd.save()
            dbv = VehiclePosition(
                oid = entity.id,
                is_deleted = entity.is_deleted,
                feed_message = dbfm,
                current_status = v.current_status,
                current_stop_sequence = v.current_stop_sequence,
                congestion_level = v.congestion_level,
                trip = dbtd,
                vehicle = dbvd,
                stop_id = v.stop_id,
                position = dbp,
                timestamp = v.timestamp)
            dbv.save()
        print "Waiting on Timeout"
        time.sleep(feed.update_timeout)
