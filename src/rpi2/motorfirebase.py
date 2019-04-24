from datetime import datetime
import time
import RPi.GPIO as GPIO
from libdw import pyrebase

url = "(my-firebase-url)"
apikey = "(my-url-key)"

config = {
    "apiKey": apikey,
    "databaseURL": url,
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

#servo setup
MAXTURN = 72
SPEED = 2
servoPIN = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
p = GPIO.PWM(servoPIN, 300) # GPIO 17 for PWM with 50Hz
p.start(0) # Initialization
time.sleep(1)
#aluminimium bracket on window for status locked
aluminPIN = 22
GPIO.setmode(GPIO.BCM)
GPIO.setup(aluminPIN, GPIO.IN, GPIO.PUD_UP)

if GPIO.input(aluminPIN) == 1: #no connection / no aluminum connection
    db.child("Sensors").child("Window").child("Status").set("Open")
    
else:
    db.child("Sensors").child("Window").child("Status").set("Closed")
    
try:
    while True:
        signal= db.child("Sensors").child("Raindrop").child("Status").get()
        open_amount = db.child("open_amount").get().val()
        
        if GPIO.input(aluminPIN) == 1: #no connection / no aluminum connection
            db.child("Sensors").child("Window").child("Status").set("Open")
            
        else:
            db.child("Sensors").child("Window").child("Status").set("Closed")
        
        wind = db.child("Sensors").child("Window").child("Status").get()
        
        if signal.val() == "It is raining" and wind.val() =="Open":
            print ("Closing Window")
            for dc in range(0, MAXTURN, SPEED):
                print(dc)
                p.ChangeDutyCycle(dc)
                time.sleep(0.1)
                
        elif signal.val()=="It is not raining" and wind.val()=="Closed":
            print ("Opening Window")
            for dc in range(MAXTURN, 11-open_amount, -SPEED):
                p.ChangeDutyCycle(dc)
                print(dc)
                time.sleep(0.1)

            db.child("Sensors").child("Window").child("Status").set("Open")
            
        time.sleep(1)

except KeyboardInterrupt:
    print("\nUser Halt!")

finally:
    p.stop()
    GPIO.cleanup()