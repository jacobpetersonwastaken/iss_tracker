import tkinter
from tkinter import *
from datetime import *
from time import time
import requests
from tkinter import messagebox
from datetime import datetime
import notification
from geopy import distance
import math


class ISS_GUI:
    times = []

    def __init__(self):
        HEIGHT = 600
        WIDTH = 600
        self.iss_long = 0
        self.iss_lat = 0
        self.iss_measurements = []
        self.iss_time_measure = []
        self.iss_speeds = []
        self.iss_mph = 69
        self.api_key = 'ISS_KEY'
        self.geocoding_api_url = f'https://maps.googleapis.com/maps/api/geocode/json?'
        self.sunset_api = 'https://api.sunrise-sunset.org/json'

        self.window = Tk()
        self.sunrise_photo = PhotoImage(file='images/sunrise.png')
        self.bg_img = Label(image=self.sunrise_photo)
        self.bg_img.grid(row=0, column=0, rowspan=10, columnspan=10, pady=30, padx=30)

        self.window.config(height=HEIGHT, width=WIDTH)
        self.window.title('iss location')

        self.sun_label = Label(text=f'Sunrise at N/a\nSunset at N/a', font=('Ariel', 11, 'bold'), wraplength=250,
                               justify='center')
        self.sun_label.grid(row=0, column=0, pady=(30, 0), padx=(20, 0))

        self.iss_loc_label = Label(text=f'International Space Station current\nLatitude: '
                                        f'{self.iss_lat}\nLongitude: {self.iss_long}\n'
                                        f'Iss mph: {420}',
                                   font=('Ariel', 11, 'bold'), wraplength=250,
                                   justify='center')

        self.iss_loc_label.grid(row=0, column=1, columnspan=5, pady=(30, 0), padx=(20, 0))

        long_label = Label(text='Longitude:', font=('Ariel', 11, 'bold'))
        long_label.grid(row=8, column=0)
        self.long_entry = Entry(width=20)
        self.long_entry.grid(row=8, column=1)

        lat_label = Label(text='Latitude:', font=('Ariel', 11, 'bold'))
        lat_label.grid(row=7, column=0)
        self.lat_entry = Entry(width=20)
        self.lat_entry.grid(row=7, column=1)

        location_search_label = Label(text='Location:', font=('Ariel', 11, 'bold'))
        location_search_label.grid(row=6, column=0)
        self.location_entry = Entry(width=20)
        self.location_entry.grid(row=6, column=1)

        self.info_label = Label(text='Enter in the longitude and latitude below. ', font=('Ariel', 11, 'bold'),
                                wraplength=250,
                                justify='center')
        self.info_label.grid(row=5, column=0, columnspan=4, pady=(30, 0))

        """Buttons"""
        search_button = Button(text='search', command=self.btn_get_location)
        search_button.grid(row=10, column=1, columnspan=4, pady=(0, 30))

        loc_search_button = Button(text='Find', command=self.btn_search_lat_long)
        loc_search_button.grid(row=6, column=2)
        self.get_iss_loc()

    def btn_get_location(self):
        """Gets the long and lat entries sets sunrise/set label and
        checks how close iss is to current input location"""
        if len(self.long_entry.get()) == 0 and len(self.lat_entry.get()) == 0:
            tkinter.messagebox.showwarning(title='Info', message='You must fill in both entries below.')
        else:
            self.get_sunrise_data()
            if not self.check_iss_proximity():
                self.window.after(60000, self.check_iss_proximity())

    def btn_search_lat_long(self):
        """Gets long/lat for the location entered and inserts it into label"""
        if len(self.location_entry.get()) == 0:
            messagebox.showwarning(title='Info', message='You must fill in both entries below.')
        else:
            parameters = {
                'address': self.location_entry.get(),
                'key': self.api_key
            }
            r = requests.get(self.geocoding_api_url, params=parameters)
            r.raise_for_status()
            data = r.json()
            results = data['results'][0]['geometry']['location']
            self.lat_entry.insert(0, results['lat'])
            self.long_entry.insert(0, results['lng'])

    def utc_to_local(self, utc_datetime):
        """Changes utc time to local"""
        exchange = (datetime.fromtimestamp(time()) - datetime.utcfromtimestamp(time())) + \
                   (datetime.fromisoformat(utc_datetime))
        return exchange

    def get_sunrise_data(self):
        """Grabs user input lat long and gets sunrise and sunset """
        user_searched_lat = int(round(float(self.lat_entry.get()), 0))
        user_searched_long = int(round(float(self.long_entry.get()), 0))
        parameters = {
            'lat': user_searched_lat,
            'lng': user_searched_long,
            'formatted': 0
        }
        r = requests.get(self.sunset_api, params=parameters)
        r.raise_for_status()
        data = r.json()
        sunrise_utc = data['results']['sunrise']
        sunrise_local = datetime.strftime(self.utc_to_local(sunrise_utc), '%I:%M:%S %p')
        sunset_utc = data['results']['sunset']
        sunset_local = datetime.strftime(self.utc_to_local(sunset_utc), '%I:%M:%S %p')

        self.sun_label['text'] = f'Sunrise at {sunrise_local}\nSunset at {sunset_local}'

    def check_iss_proximity(self):
        """Checks how close iss is to input long/lat"""
        self.get_iss_loc()
        user_lat = float(self.lat_entry.get())
        user_long = float(self.long_entry.get())
        print(self.iss_long, self.iss_long)
        if (user_lat - 5) <= self.iss_lat <= (user_lat + 5) and (user_long - 5) <= self.iss_long <= (user_long + 5):

            notification.send_iss_notification(self.iss_lat, self.iss_long)
            self.info_label['text'] = 'It looks like the space station is above your head right now! We just ' \
                                      'sent you an email.'
            return False
        else:
            self.iss_loc_label['text'] = f'International Space Station current\nLatitude: {self.iss_lat}\n' \
                                         f'Longitude: {self.iss_long}'
            self.info_label['text'] = f'It looks like the space station isnt above your head yet.\n' \
                                      f'We will continue to monitor its location every minute and ' \
                                      f'update you if its in your area!'
            return True

    def get_iss_loc(self):
        """Gets the long lat of iss and calculates its mph."""
        ISS_API_URL = 'http://api.open-notify.org/iss-now.json'
        r = requests.get(ISS_API_URL)
        data = r.json()
        iss_lat = float(data['iss_position']['latitude'])
        iss_long = float(data['iss_position']['longitude'])
        self.iss_lat = iss_lat
        self.iss_long = iss_long
        # calulcate time
        self.times.append(datetime.now())
        self.iss_measurements.append([iss_lat, iss_long])

        if len(self.times) > 2:
            self.times.pop(0)
        if len(self.iss_measurements) > 2:
            self.iss_measurements.pop(0)
        if len(self.iss_measurements) < 2 and len(self.times) < 2:
            self.iss_mph = "Calculating..."
        else:
            travel_dist = math.ceil(distance.distance(self.iss_measurements[0], self.iss_measurements[1]).miles)

            travel_time = (self.times[1] - self.times[0]).total_seconds()
            iss_speed = (travel_dist / travel_time * 60) * 60

            self.iss_speeds.append(iss_speed)
            iss_mph = round(sum(self.iss_speeds) / len(self.iss_speeds), 2)
            self.iss_mph = '{:,}'.format(iss_mph)

        self.iss_loc_label[
            'text'] = f'International Space Station current\nLatitude: {iss_lat}\nlongitude: {iss_long}\nAvg ss speed: {self.iss_mph}mph'
        self.window.after(1000, self.get_iss_loc)
