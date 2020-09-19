# TrafficFiles
A repository for my intelligent traffic controller with raspberry pi and TfLite project.
This program uses a TensorFlow Lite object detection model to perform object
detection on a folder full of traffic images. It gets the number of cars
detected on each traffic and return it in a dictionary to the traffic controller.
The traffic controller either controls to traffic based on the model's output or switches to the timer-based on - controls the traffic on timer-based

This code is based off the TensorFlow Lite object detection on Raspberry pi tutorial by EdgeElectronics at:
https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi

I made the whole file a function so that I can call it in my traffic file the command line
I modified the parser args and the return values to suit my needs and reduce the processing time
I also removed the lines of codes I didn't need, modified it to not draw boundary boxes and only get labels using OpenCV.

# How to Set Up and Run TensorFlow Lite Object Detection Models on your System
Setting up TensorFlow Lite has been made easier with virutal environemnt. I have installed the required packages and the python version (python3.7) I used in a virtual environment! 
These are the steps needed to get started:

1. Clone the repository
2. Open the cloned repository folder in git or command terminal
3. Activate the tflite1-env virtual environment by typing 
```
source tflite1-env/Scripts/activate
```
4. Run the traffic controller program by typing:
```
python -u traffic_final_demo.py --operator=Mem --time=2
```

The -u argument runs the program in batch mode

The --operator argument tells the script the name of the person running the program. **Replace `Mem` with your other name of choice**

The --time argument tells the script the number of time you want the traffic controller to run iteratively. **Replace `2` with other positive number integer**

The program was modified for this demo to output a traffic control light sequence in plain english which would have been visible with Raspberry pi and LEDs. *The traffic_final.py file works with LEDs in Raspberry pi to controller LED traffic lights*
