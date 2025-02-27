# I-Open-at-the-Close

## Motivation
Ever left the hostel room in a hurry, only to realise that you forgot to close the windows half way across the campus? Our solution provides ease of mind to users as you won't ever get your room wet due to the weather!

## Solution
Our solution uses a raindrop sensor to detect the weather and initialise sequence to close window. When rain is detected, motor turns clockwise and the window is pulled shut. We will detect if window is closed by checking for a positive input signal which connects to the power source on the window sill via an aluminium strip on the window sill. When rain is not detected, motor turns anticlockwise and opens Ato ventilate the room.

We use Google Firebase to allow for easy customisation for users. Users will be able to customize their preferences of how wide they prefer their window to be open as well in different weathers.

In addition, notification messages will be sent to the user's Kivy upon successfully closing the window. After duration elapsed and window sill does not receive positive input, a notification will be sent to user informing anomaly. 

![read_me_overall_DESCR](https://github.com/shiyingt/I-Open-at-the-Close/blob/master/images/Screenshot%20from%202019-04-10%2022-33-46.png)


## Overall Structure
src\
├──rpi1\
│   ├──waterfirebase.py\
├──rpi2\
│   ├──motorfirebase.py\
├──kivy
