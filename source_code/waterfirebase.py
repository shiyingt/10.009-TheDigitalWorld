from datetime import datetime
import time
import RPi.GPIO as GPIO
from libdw import pyrebase

url = "https://test-firebase-92972.firebaseio.com/"
apikey = "AIzaSyDV8sHwqReBhnSzPRLsonkEOo9kAf8GAFE"

config = {
    "apiKey": apikey,
    "databaseURL": url,
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

#water sensor setup
water_sensor = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(water_sensor, GPIO.IN)

#raining = False
try:
    while True:
        time.sleep(0.4)
        active_time = time.time()
        dt = datetime.now()
        print(dt)
        print(GPIO.input(water_sensor))
        if GPIO.input(water_sensor):
                #raining = False
                print("It is not raining")
                db.child("Sensors").child("Raindrop").child("Status").set("It is not raining")
                db.child("Sensors").child("Raindrop").child("Time").set(active_time)
                
        else:
                print("it is raining")
                db.child("Sensors").child("Raindrop").child("Status").set("It is raining")
                db.child("Sensors").child("Raindrop").child("TimeStart").set(active_time)

except KeyboardInterrupt:

        print("\nUser Halt!")

finally:

        GPIO.cleanup()
