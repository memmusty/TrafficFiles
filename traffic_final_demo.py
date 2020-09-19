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

import argparse

    # Define and parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--modeldir', help='Folder the .tflite file is located in',
                        default='Sample_TFLite_model')
parser.add_argument('--graph', help='Name of the .tflite file, if different than detect.tflite',
                        default='detect.tflite')
parser.add_argument('--labels', help='Name of the labelmap file, if different than labelmap.txt',
                        default='labelmap.txt')
parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects',
                        default=0.3)
parser.add_argument('--image', help='Name of the single image to perform detection on. To run detection on multiple images, use --imagedir',
                        default=None)
parser.add_argument('--imagedir', help='Name of the folder containing images to perform detection on. Folder must contain only images.',
                        default='Traffic_images')
parser.add_argument('--edgetpu', help='Use Coral Edge TPU Accelerator to speed up detection',
                        default=None) #change to True to use edetpu
parser.add_argument('--operator', help='The name of the software operator',
                        default='Unspecified')
parser.add_argument('--time', help='The number of times the program should be executed',
                        default='1')
                        

args = parser.parse_args()

MODEL_NAME = args.modeldir
GRAPH_NAME = args.graph
LABELMAP_NAME = args.labels
min_conf_threshold = float(args.threshold)
use_TPU = args.edgetpu


# Parse input image name and directory.
IM_NAME = args.image
IM_DIR = args.imagedir
OPERATOR_NAME = args.operator
ITERATIONS = int(args.time)

import sys
#from gpiozero import LED
#from picamera import PiCamera
from time import sleep
from Mem_detection_image_demo import objectsCount

##setting up the camera
#camera = PiCamera()
#camera.rotation = 180
print("Traffic controller started by: " + OPERATOR_NAME)

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
    labels = objectsCount(MODEL_NAME, GRAPH_NAME, LABELMAP_NAME, min_conf_threshold, use_TPU, IM_NAME, IM_DIR)

    #save the items in labels into carCounts with descriptive dict keys
    for key, val in labels.items():
        CarCounts["Traffic "+key[-5]] = val
    print("Result - " +str(CarCounts))

    ##example of the carCounts value
    #{'traffic4': 3, 'traffic2': 19}
    return(CarCounts)

##Creates a Traffic object; each object has yellow, green, and red traffic light
class LED:
    def __init__(self, color, number):
        self.color = color
        self.number = number

    def on(self):
        """
        This function turns on the green light of the traffic and turn off the yellow and red lights
        """
        print("Traffic " +str( self.number) + " " + self.color + " is on")
    
    def off(self):
        """
        This function turns on the green light of the traffic and turn off the yellow and red lights
        """
        print("Traffic " +str( self.number) + " " + self.color + " is off")

##Creates a Traffic object; each object has yellow, green, and red traffic light
class Traffic:
    def __init__(self, red, yellow, green):
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
        print("\n")

    def wait(self):
        """
        This method turns on the yellow light of the traffic and turn off the green and red lights
        """
        self.green.off()
        self.yellow.on()
        self.red.off()
        print("\n")

    def stop(self):
        """
        This method turns on the red light of the traffic and turn off the yellow and green lights
        """
        self.green.off()
        self.yellow.off()
        self.red.on()
        print("\n")

    def reset(self):
        """
        This method turns off all the traffic lights
        """
        self.green.off()
        self.yellow.off()
        self.red.off()
        print("\n")


##creates Road object instances
##Each road traffic has a green, red, and yellow LED which are connected to the called rpi pins
traffic1 = Traffic(LED("red",1), LED("yellow",1), LED("green", 1))
traffic2 = Traffic(LED("red",2), LED("yellow",2), LED("green", 2))


##The pass functions turn on the green LED of the passed traffic and turn on the red LEDs of the other traffics
def passTraffic1():
    traffic1.go()
    traffic2.stop()
    sleep(2)

def passTraffic2():
    traffic1.stop()
    traffic2.go()
    sleep(2)

def wait():
    """
    The wait function turns on the yellow LEDs of all the traffics
    """
    print("Processing traffic Data\n")
    traffic1.wait()
    traffic2.wait()

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


##This loop will run iteratively for the specified number once the program is executed 
i = 0
while i<ITERATIONS:
    try:
        #uncomment the next line and comment the following line to activate the timer mode for testing
        #carCounts = ""
        wait()
        #gets the number of cars on each traffic
        carCounts = getImageCount()

        #passes the traffic with the highest number of cars
        if carCounts:
            #get the name of the traffic with the highest number of cars in the carCounts dictionary
            Max = max(carCounts, key=carCounts.get)

            if Max == "traffic1":
                print("Passing " + Max.capitalize())
                print("\n")
                passTraffic1()
            else:
                print("Passing" + Max.capitalize())
                print("\n")
                passTraffic2()
            wait()

        #Activates timer-based control if there are error getting the images or processing them
        else:
            print("Error fetching images from camera\nTimer mode activated...")
            timerControl()

    ##exits execution on Ctrl+C
    except (KeyboardInterrupt, SystemExit):
        traffic1.reset()
        traffic2.reset()
        sys.exit()
    i+=1