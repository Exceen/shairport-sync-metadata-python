#!/usr/bin/python
import paho.mqtt.client as mqtt
import os
import time
from datetime import date
from datetime import timedelta
from shutil import copyfile
from multiprocessing import Process

# possible problems:
# skipping multiple songs in a short time
# check what happens when there is no album artwork set
# what to do when artwork loading takes too long?

base_path = '/home/pi/scripts/github/media_frame/data/music/'

wait_for_artwork_process = []

def set_track_information(state, track_information):
    global wait_for_artwork_process

    if state == 'pause':
        track_information = 'PAUSED ' + track_information

    path = base_path + 'current_track.txt'

    previous_track = None
    with open(base_path + 'current_track.txt', 'r') as f:
        previous_track = f.read()

    if previous_track != track_information:
        f = open(path, 'w')
        f.write(track_information)
        f.close()

        # if os.path.isfile(base_path + 'is_active'):
        process = Process(target=set_default_artwork, args=( ))
        process.start()
        wait_for_artwork_process.append(process)

    if state == 'pause':
        # frame_next('track pause')

        print('paused')
        print('starting new PictureFrame for photos')
        kill_wait_for_artwork_process()
        os.system('/home/pi/scripts/github/media_frame/scripts/change_media_to_photos.sh')


def set_default_artwork():
    global wait_for_artwork_process

    time.sleep(5)
    remove_old_artworks()
    copyfile(base_path + 'default.jpg', base_path + 'artwork/default.jpg')
    frame_next('no artwork')

def set_album_artwork(path):

    pic_dir = base_path + 'artwork/'
    newArtworkPath = os.path.join(pic_dir, os.path.basename(path))
    copyfile(path, newArtworkPath)
    remove_old_artworks(newArtworkPath)
    kill_wait_for_artwork_process()
    frame_next('artwork')

####################################

def kill_wait_for_artwork_process():
    global wait_for_artwork_process
    for p in wait_for_artwork_process:
        if p.is_alive():
            p.kill()
            print('killed no artwork process')
        wait_for_artwork_process.remove(p)


def remove_old_artworks(exceptFile = None):
    pic_dir = base_path + 'artwork/'
    files_to_remove = []
    for f in os.listdir(pic_dir):
        full_path = os.path.join(pic_dir, f)
        if os.path.isfile(full_path):
            if exceptFile is None or full_path != exceptFile:
                files_to_remove.append(full_path)
    for path in files_to_remove:
        os.remove(path)

def frame_next(info = ''):

    if os.path.isfile(base_path + 'is_active'):
        client = mqtt.Client()
        client.connect("localhost", 1883, 60)
        client.publish("frame/next")
        client.disconnect()
        print('frame/next ' + info)
    else:
        print('frame/next ' + info)
        kill_wait_for_artwork_process()
        print('starting new PictureFrame for music')
        os.system('/home/pi/scripts/github/media_frame/scripts/change_media_to_music.sh')

#   client.username_pw_set(config.MQTT_LOGIN, config.MQTT_PASSWORD)
#   client.subscribe("frame/date_from", qos=0) # needs payload as 2019:06:01 or divided by ":", "/", "-" or "."
#   client.subscribe("frame/date_to", qos=0)
#   client.subscribe("frame/time_delay", qos=0) # payload seconds for each slide
#   client.subscribe("frame/fade_time", qos=0) # payload seconds for fade time between slides
#   client.subscribe("frame/shuffle", qos=0) # payload on, yes, true (not case sensitive) will set shuffle on and reshuffle
#   client.subscribe("frame/quit", qos=0)
#   client.subscribe("frame/paused", qos=0) # payload on, yes, true pause, off, no, false un-pause. Anything toggle state
#   client.subscribe("frame/back", qos=0)
#   client.subscribe("frame/next", qos=0)
#   client.subscribe("frame/subdirectory", qos=0) # payload string must match a subdirectory of pic_dir
#   client.subscribe("frame/delete", qos=0) # delete current image, copy to dir set in config
#   client.subscribe("frame/text_on", qos=0) # toggle file name on and off. payload text show time in seconds
#   client.subscribe("frame/date_on", qos=0) # toggle date (exif if avail else file) on and off. payload show time
#   client.subscribe("frame/location_on", qos=0) # toggle location (if enabled) on and off. payload show time
#   client.subscribe("frame/text_off", qos=0) # turn all name, date, location off
#   client.subscribe("frame/text_refresh", qos=0) # restarts current slide showing text set above


