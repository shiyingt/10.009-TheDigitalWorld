import pyrebase
from time import sleep
import requests
from datetime import datetime

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle

#change typefaces for better look, give color for button
Builder.load_string("""
<Label> :
	font_name : 'Roboto'
<Button> :
	font_name : 'Roboto'
	background_color : (0.95, 0.8, 0.0, 1)
""")

#your firebase database
url = "yourfirebaseurl"
apikey = "yourapikey"

config = {
    "apiKey": apikey,
    "databaseURL": url,
}

#initialize firebase object
firebase = pyrebase.initialize_app(config)
db = firebase.database()

#at upper changi north
humidity_threshold = 70  #below which rain is theoretically1 implausible
area_code = "S24" #upper changi area code for weather fetch from data.gov.sg

class MenuScreen(Screen):
	def __init__(self, **kwargs):
		Screen.__init__(self, **kwargs)

		#fetch weather and rainfall info from data.gov.sg
		_weather = self.fetch_weather()
		_rainfall = self.fetch_rain()
		#fetch rain sensor and window sensor status from firebase
		_status = db.child("Sensors").child("Raindrop").child("Status").get().val()
		_window = db.child("Sensors").child("Window").child("Status").get().val()

		if not _window:
			_window = "Unavailable"

		if not _status:
			_status = "Unavailable"
		else:
			_status = _status[6:] # get the plain status : raining or not raining

		#smart analysis degree 1
		_smart = "Nothing suspicious" #if condition below not satisfied
		
		if _status == "raining" and _weather != "Unavailable" and float(_weather) < humidity_threshold: #if humidity is below 70 at upper changi but it is raining
			_smart = "(It may actually not be raining)" 	#then it may be a false positive


		#build kivy interface
		root = FloatLayout()

		#add background image
		with self.canvas.before:
			gray = 0.7
			Color(gray, gray, gray, 0.5)
			self.rect = Rectangle(size=self.size,
			                       pos=self.pos, source="bg.jpg")

		#make image responsive
		def update_rect(instance, value):
		    instance.rect.pos = instance.pos
		    instance.rect.size = instance.size


		# listen to size and position changes
		self.bind(pos=update_rect, size=update_rect)

		#top half of main screen
		layout = BoxLayout(orientation='vertical')
		layout1 = BoxLayout(size_hint = (1, .3))
		l1 = Label(text = "SUTD\nSmart\nWindow" , halign = 'center', font_size = 70, size_hint = (1, .5))
		layout.add_widget(l1)
		l2 = Label(text = "Rain sensor status : {status}\n Window status : {window}\n Singapore weather at your\nlocation & prediction : {weather}\n Rainfall : {rain}\n Smart detect : {smart}".format(status = _status, window = _window, weather = _weather, rain = _rainfall, smart = _smart), halign='center', font_size = 15)
		self.details_label = l2
		layout1.add_widget(l2)
		layout.add_widget(layout1)

		#update button
		self.but_up = Button(text="Update values", on_press = self.update_values, font_size = 17, size_hint = (1, .07))
		layout.add_widget(self.but_up)

		#botton half of main screen
		layout2 = BoxLayout(size_hint = (1, .13))
		button2 = Button(text='Settings', font_size = 30, on_press = self.change_to_setting)
		button3 = Button(text='Quit', font_size = 30, on_press = self.quit_app)

		#stitch everything together
		layout2.add_widget(button2)
		layout2.add_widget(button3)
		layout.add_widget(layout2)
		root.add_widget(layout)
		self.add_widget(root)


	def update_values(self, value):
		#initialise
		_status = 'Unavailable'
		_window = 'Unavailable'
		_weather = 'Unavailable'
		_rainfall = 'Unavailable'

		#fetch from government
		_weather = self.fetch_weather()
		_rainfall = self.fetch_rain()
		#fetch from firebase
		_status = db.child("Sensors").child("Raindrop").child("Status").get().val()
		_window = db.child("Sensors").child("Window").child("Status").get().val()

		#smart analysis degree 1
		_smart = "Nothing suspicious"
		if _status == "raining" and _weather != "Unavailable" and float(_weather) < humidity_threshold: #if humidity is below 70 at upper changi but it is raining
			_smart = "(It may actually not be raining)"  	#then it might be a false positive

		if not _status:
			_status = "Unavailable"
		else:
			_status = _status[6:]   #slice the important info only
		if not _window:
			_window = "Unavailable"

		new_string = "Rain sensor status : {status}\n Window status : {window}\n Singapore weather at your\nlocation & prediction : {weather}\n Rainfall : {rain}\n Smart detect : {smart}".format(status = _status, window = _window, weather = _weather, rain = _rainfall, smart = _smart)
		
		#if previous and current same data, there is (no change). otherwise, it is updated.
		if self.details_label.text == new_string:
			self.but_up.text = "Update values (no change)"
		else :
			self.details_label.text = new_string
			self.but_up.text = "Update values (updated)"


	def fetch_weather(self):
		#calculate time parameters
		dt = self.date_time()
		#use data.gov.sg API
		r = requests.get("https://api.data.gov.sg/v1/environment/relative-humidity?date_time=" + dt)
		reading = r.json()
		reading = reading['items'][0]['readings']
		#look for upper changi data
		for entry in reading:
			if entry["station_id"] == "S24": # Location code for upper changi road north
				return '{0}% Humidity'.format(entry["value"])
		return 'Unavailable'  #if no upper changi data

	def fetch_rain(self):
		#calculate time parameters
		dt = self.date_time()
		#use data.gov.sg API
		r = requests.get("https://api.data.gov.sg/v1/environment/rainfall?date_time=" + dt)
		reading = r.json()['items'][0]['readings']
		#look for upper changi data
		for entry in reading:
			if entry["station_id"] == 'S24':
				return '{0}'.format(entry['value'])
		return 'Unavailable' #if no upper changi data

	def date_time(self):
		#get the date and time right now
		dt = str(datetime.now()).strip()
		#add the 'T' for proper datetime query format
		dt = dt[:-7].replace(' ','T')
		#code sequence to modify date time
		'''
		dt = list(dt)
		dt[3] = chr(ord(dt[3]) - 1)  #get data for last year today
		dt[6] = chr(ord(dt[6]) + 3)  #roll back many months for demo, since this week somehow no data is available
		dt = ''.join(dt)
		'''
		#add time zone for singapore
		dt += '+08:00'
		#format for ASCII / what is appropriate for URL 
		dt = dt.replace(':', '%3A')
		dt = dt.replace('+', '%2B')
		return dt

	def change_to_setting(self, value):
		self.manager.transition.direction = 'left'
		# modify the current screen to settings screen
		self.manager.current = "settings"

	def quit_app(self, value):
		App.get_running_app().stop()


class SettingsScreen(Screen):
	def __init__(self, **kwargs):
		Screen.__init__(self, **kwargs)
		root = FloatLayout()

		#add background image
		with self.canvas.before:
			gray = 0.7
			Color(gray, gray, gray, 0.5)
			self.rect = Rectangle(size=self.size,
			                       pos=self.pos, source="bg2.jpg")

		#make image responsive
		def update_rect(instance, value):
		    instance.rect.pos = instance.pos
		    instance.rect.size = instance.size

		# listen to size and position changes
		self.bind(pos=update_rect, size=update_rect)

		#fetch current data for below from firebase
		current_contact = db.child("phone").get().val()
		current_pull_amount = int(db.child("SPEED").get().val() / 8 * 100)

		#build interface
		layout = BoxLayout(orientation = 'vertical')
		#make top half
		layout1 = BoxLayout()
		l1 = Label(text = 'Contact\nDetails:', font_size = 35)
		i1 = TextInput(text = str(current_contact), font_size = 20)
		self.contact_input = i1
		layout2 = BoxLayout()
		l2 = Label(text = 'How fast to\nopen window:\n(0 <= x <= 100)', font_size = 30)
		i2 = TextInput(text = str(current_pull_amount), font_size = 20)
		self.pull_input = i2

		#stitch top half together
		layout1.add_widget(l1)
		layout1.add_widget(i1)
		layout2.add_widget(l2)
		layout2.add_widget(i2)

		#make bottom half (buttons)
		layout3 = BoxLayout(size_hint = (1, 0.14))
		b1 = Button(text = 'Save', on_press = self.save_settings)
		self.save_button = b1
		b2 = Button(text = 'Back to menu', on_press = self.change_to_menu)
		layout3.add_widget(b1)
		layout3.add_widget(b2)

		#stitch everything together
		layout.add_widget(layout1)
		layout.add_widget(layout2)
		layout.add_widget(layout3)
		root.add_widget(layout)
		self.add_widget(root)


	def save_settings(self, value):
		#fetch input values for contact and speed
		#variable pull_amount originally for window pull amount for open phase, changed to speed
		phone = self.contact_input.text.replace(' ', '').replace(' \n', '')
		pull_amount = self.pull_input.text.replace(' ', '').replace(' \n', '')

		#error flag
		err = False
		#phone number must contain integers only
		if  phone.isnumeric():
			db.child("phone").set(int(phone))
		else:
			self.contact_input.text = "Error! Contact must be a phone number"
			err = True
		#speed must be a percentage value in integer
		if pull_amount.isnumeric() and int(pull_amount) >= 0 and int(pull_amount) <= 100 :
			db.child("SPEED").set(int(float(pull_amount)/100 * 8))	#from 0 to 100
		else:
			self.pull_input.text = "Error ! Speed must be an integer from 0 to 100"
			err = True
		#status message depends on error status
		if not err:
			self.save_button.text = 'Save (Saved)'
		else:
			self.save_button.text = 'Save (Error Saving)'

	def change_to_menu(self, value):
		self.manager.transition.direction = 'right'
		# modify the current screen to main menu screen
		self.manager.current = "menu"


class SwitchScreenApp(App):
	def build(self):
		sm = ScreenManager()
		ms = MenuScreen(name='menu')
		st = SettingsScreen(name='settings')
		sm.add_widget(ms)
		sm.add_widget(st)
		sm.current = 'menu'
		return sm


if __name__ == '__main__':
    SwitchScreenApp().run()



