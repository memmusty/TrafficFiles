# Write your code here :-)
import sys
from gpiozero import LED
from picamera import PiCamera
from time import sleep
from Mem_detection_image import objectsCount


camera = PiCamera()
camera.rotation = 180

def captureImage():
    camera.start_preview()
    for i in range(1,5):
        sleep(2)
        camera.capture('/home/pi/tflite1/Traffic_images/cars%s.jpg' % i)
    camera.stop_preview()


def getImageCount():
    #captureImage()
    CarCounts = {}
    labels = objectsCount()
    for key, val in labels.items():
        CarCounts["Road"+key[-5]] = val
    print(CarCounts)
    return(CarCounts)
getImageCount()

class Road:
    def __init__(self, green, yellow, red):
        self.green = green
        self.yellow = yellow
        self.red = red
    def go(self):
        self.green.on()
        self.yellow.off()
        self.red.off()
    def wait(self):
        self.green.off()
        self.yellow.on()
        self.red.off()
    def stop(self):
        self.green.off()
        self.yellow.off()
        self.red.on()
    def reset(self):
        self.green.off()
        self.yellow.off()
        self.red.off()

road1 = Road(LED(17), LED(27), LED(22))
road2 = Road(LED(14), LED(15), LED(18))
road3 = Road(LED(25), LED(8), LED(7))
road4 = Road(LED(16), LED(20), LED(21))

while True:
    try:
        road1.go()
        road3.go()
        road2.stop()
        road4.stop()
        sleep(1)
        road1.wait()
        road2.wait()
        road3.wait()
        road4.wait()
        sleep(1)
        road1.stop()
        road3.stop()
        road2.go()
        road4.go()
        sleep(1)
        road1.wait()
        road2.wait()
        road3.wait()
        road4.wait()
        sleep(1)

    except (KeyboardInterrupt, SystemExit):
        road1.reset()
        road2.reset()
        road3.reset()
        road4.reset()
        sys.exit()