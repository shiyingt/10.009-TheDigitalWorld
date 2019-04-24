from datetime import datetime
import time
import RPi.GPIO as io
from libdw import pyrebase

url = "(my-firebase-url)"
apikey = "(my-url-key)"

config = {
    "apiKey": apikey,
    "databaseURL": url,
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
root=db.child("/").get()

#water sensor setup
water_sensor = 26
io.setmode(io.BCM)
io.setup(water_sensor, io.IN)

#raining = False
try:
    while True:
        active_time = time.time()
        print(io.input(water_sensor))
        if io.input(water_sensor) ==0:
                #raining = False
                
                db.child("Sensors").child("Raindrop").child("Status").set("It is raining")
                db.child("Sensors").child("Raindrop").child("Time").set(active_time)
                
        else:   
                #new = None
                #if not raining:
                #        raining = True

                #active_time = str(datetime.now())
                #ind = active_time.find(' ') + 1
                #active_time = active_now[ind, ind + 6]
                db.child("Sensors").child("Raindrop").child("Status").set("It is not raining")
                db.child("Sensors").child("Raindrop").child("TimeStart").set(active_time)
                #print(active_time)
                #for _ in range(5):  #winds up window
                #    p.ChangeDutyCycle(5)
                #    time.sleep(0.5)

except KeyboardInterrupt:

        print("\nUser Halt!")

finally:

        io.cleanup()
