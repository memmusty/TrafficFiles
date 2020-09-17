##Pseudocode
#while waiting, capture road images
#get car counts
#determine the road with the maximum cars
#pass the road with the max cars
#make others stop
#if no max or not image
#pass any road
#wait
#iterate

##import relevant python libraries
import sys
from gpiozero import LED
from picamera import PiCamera
from time import sleep
from Mem_detection_image import objectsCount

##setting up the camera
camera = PiCamera()
camera.rotation = 180

def captureImage():
    """
    This function captures 4 images via the piCamera and save them in the Traffic_image folder
    """
    camera.start_preview()
    for i in range(1,5):
        sleep(2)
        camera.capture('/home/pi/tflite1/Traffic_images/cars%s.jpg' % i)
    camera.stop_preview()


def getImageCount():
    """
    This function gets the images in the Traffic_images folder, and pass them to the object detection model."

    It returns the number of cars detected in the images in a dictionary.
    """
    #uncommented the next line of code to replace the traffic images in the folder with images from camera
    #captureImage()

    #instantiating the dictionary where the object detection output will be saved in
    CarCounts = {}

    #calls the object detection model to process all the images in the Traffic_image folder and save the returned value in labels
    labels = objectsCount()

    #save the items in labels into carCounts with descriptive dict keys
    for key, val in labels.items():
        CarCounts["traffic"+key[-5]] = val
    print(CarCounts)

    ##example of the carCounts value
    #{'traffic4': 3, 'traffic2': 19, 'traffic1': 0, 'traffic3': 17}
    return(CarCounts)


##Creates a Traffic object; each object has yellow, green, and red traffic light
class Traffic:
    def __init__(self, green, yellow, red):
        self.green = green
        self.yellow = yellow
        self.red = red

    def go(self):
        """
        This function turns on the green light of the traffic and turn off the yellow and red lights
        """
        self.green.on()
        self.yellow.off()
        self.red.off()

    def wait(self):
        """
        This method turns on the yellow light of the traffic and turn off the green and red lights
        """
        self.green.off()
        self.yellow.on()
        self.red.off()

    def stop(self):
        """
        This method turns on the red light of the traffic and turn off the yellow and green lights
        """
        self.green.off()
        self.yellow.off()
        self.red.on()

    def reset(self):
        """
        This method turns off all the traffic lights
        """
        self.green.off()
        self.yellow.off()
        self.red.off()


##creates Road object instances
##Each road traffic has a green, red, and yellow LED which are connected to the called rpi pins
traffic1 = Traffic(LED(17), LED(27), LED(22))
traffic2 = Traffic(LED(14), LED(15), LED(18))
traffic3 = Traffic(LED(25), LED(8), LED(7))
traffic4 = Traffic(LED(16), LED(20), LED(21))


##The pass functions turn on the green LED of the passed traffic and turn on the red LEDs of the other traffics
def passTraffic1():
    traffic1.go()
    traffic2.stop()
    traffic3.stop()
    traffic4.stop()
    sleep(2)

def passTraffic2():
    traffic1.stop()
    traffic2.go()
    traffic3.stop()
    traffic4.stop()
    sleep(2)

def passTraffic3():
    traffic1.stop()
    traffic2.stop()
    traffic3.go()
    traffic4.stop()
    sleep(2)

def passTraffic4():
    traffic1.stop()
    traffic2.stop()
    traffic3.stop()
    traffic4.go()
    sleep(2)

def wait():
    """
    The wait function turns on the yellow LEDs of all the traffics
    """
    traffic1.wait()
    traffic2.wait()
    traffic3.wait()
    traffic4.wait()

def timerControl():
    """
    This function controls the traffic on a timer based mode.

    It will called when there are issues running the image based mode.
    """
    passTraffic1()
    wait()
    sleep(1)

    passTraffic2()
    wait()
    sleep(1)

    passTraffic3()
    wait()
    sleep(1)

    passTraffic4()
    wait()
    sleep(1)


##This loop will run continuously once the program is executed
while True:
    try:
        #uncomment the next line and comment the following line to activate the timer mode for testing
        #carCounts = ""

        #gets the number of cars on each traffic
        carCounts = getImageCount()

        #passes the traffic with the highest number of cars
        if carCounts:
            #get the name of the traffic with the highest number of cars in the carCounts dictionary
            Max = max(carCounts, key=carCounts.get)

            if Max == "traffic1":
                print("passing", Max.capitalize())
                passTraffic1()
            elif Max == "traffic2":
                print("passing", Max.capitalize())
                passTraffic2()
            elif Max == "traffic3":
                print("passing", Max.capitalize())
                passTraffic3()
            else:
                print("passing", Max.capitalize())
                passTraffic4()
            wait()

        #Activates timer-based control if there are error getting the images or processing them
        else:
            print("Error fetching images from camera\nTimer mode activated...")
            timerControl()

    ##exits execution on Ctrl+C
    except (KeyboardInterrupt, SystemExit):
        traffic1.reset()
        traffic2.reset()
        traffic3.reset()
        traffic4.reset()
        sys.exit()