######## Webcam Object Detection Using Tensorflow-trained Classifier #########
#
# Author: Evan Juras
# Date: 9/28/19
# Description:
# This program uses a TensorFlow Lite object detection model to perform object
# detection on an image or a folder full of images. It draws boxes and scores
# around the objects of interest in each image.
#
# This code is based off the TensorFlow Lite image classification example at:
# https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/examples/python/label_image.py
# I added my own method of drawing boxes and labels using OpenCV.
#
#
# Modified by: Memunat Ibrahim
# Date: 5/10/2020
# Description:
# This program uses a TensorFlow Lite object detection model to perform object
# detection on a folder full of traffic images. It gets the number of cars
# detected on each traffic and return it in a dictionary.
#
# This code is based off the TensorFlow Lite object detection on Raspberry pi tutorial by EdgeElectronics at:
# https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi
#
# I made the whole file a function so that I can call it in my traffic file the command line
# I modified the parser args and the return values to suit my needs and reduce the processing time
# I also removed the lines of codes I didn't need, modified it to not draw boundary boxes and only get labels using OpenCV.


# Import packages

def objectsCount():
    import os
    import argparse
    import cv2
    import numpy as np
    import sys
    import glob
    import importlib.util

    # Define and parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--modeldir', help='Folder the .tflite file is located in',
                        default='TrafficFiles/Sample_TFLite_model')
    parser.add_argument('--graph', help='Name of the .tflite file, if different than detect.tflite',
                        default='detect.tflite')
    parser.add_argument('--labels', help='Name of the labelmap file, if different than labelmap.txt',
                        default='labelmap.txt')
    parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects',
                        default=0.3)
    parser.add_argument('--image', help='Name of the single image to perform detection on. To run detection on multiple images, use --imagedir',
                        default=None)
    parser.add_argument('--imagedir', help='Name of the folder containing images to perform detection on. Folder must contain only images.',
                        default='TrafficFiles/Traffic_images')
    parser.add_argument('--edgetpu', help='Use Coral Edge TPU Accelerator to speed up detection',
                        default=True)

    args = parser.parse_args()

    MODEL_NAME = args.modeldir
    GRAPH_NAME = args.graph
    LABELMAP_NAME = args.labels
    min_conf_threshold = float(args.threshold)
    use_TPU = args.edgetpu
    GRAPH_NAME = 'edgetpu.tflite'


    # Parse input image name and directory.
    IM_NAME = args.image
    IM_DIR = args.imagedir

    # If both an image AND a folder are specified, throw an error
    if (IM_NAME and IM_DIR):
        print('Error! Please only use the --image argument or the --imagedir argument, not both. Issue "python TFLite_detection_image.py -h" for help.')
        sys.exit()

    # If neither an image or a folder are specified, default to using 'test1.jpg' for image name
    if (not IM_NAME and not IM_DIR):
        IM_NAME = 'test1.jpg'

    # Import TensorFlow libraries
    # If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
    # If using Coral Edge TPU, import the load_delegate library
    pkg = importlib.util.find_spec('tflite_runtime')
    if pkg:
        from tflite_runtime.interpreter import Interpreter
        if use_TPU:
            from tflite_runtime.interpreter import load_delegate
    else:
        from tensorflow.lite.python.interpreter import Interpreter
        if use_TPU:
            from tensorflow.lite.python.interpreter import load_delegate


    # Get path to current working directory
    CWD_PATH = os.getcwd()

    # Define path to images and grab all image filenames
    if IM_DIR:
        PATH_TO_IMAGES = os.path.join(CWD_PATH,IM_DIR)
        images = glob.glob(PATH_TO_IMAGES + '/*')

    elif IM_NAME:
        PATH_TO_IMAGES = os.path.join(CWD_PATH,IM_NAME)
        images = glob.glob(PATH_TO_IMAGES)

    # Path to .tflite file, which contains the model that is used for object detection
    PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

    # Path to label map file
    PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

    # Load the label map
    with open(PATH_TO_LABELS, 'r') as f:
        labels = [line.strip() for line in f.readlines()]

    # Have to do a weird fix for label map if using the COCO "starter model" from
    # https://www.tensorflow.org/lite/models/object_detection/overview
    # First label is '???', which has to be removed.
    if labels[0] == '???':
        del(labels[0])

    # Load the Tensorflow Lite model.
    # If using Edge TPU, use special load_delegate argument
    if use_TPU:
        interpreter = Interpreter(model_path=PATH_TO_CKPT,
                                  experimental_delegates=[load_delegate('libedgetpu.so.1.0')])

    else:
        interpreter = Interpreter(model_path=PATH_TO_CKPT)

    interpreter.allocate_tensors()

    # Get model details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    floating_model = (input_details[0]['dtype'] == np.float32)

    input_mean = 127.5
    input_std = 127.5

    objects_list={} #create the dictionary where the traffic names and number of cars detected will be saved

    # Loop over every image and perform detection
    for image_path in images:

        # Load image and resize to expected shape [1xHxWx3]
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imH, imW, _ = image.shape
        image_resized = cv2.resize(image_rgb, (width, height))
        input_data = np.expand_dims(image_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if floating_model:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        interpreter.set_tensor(input_details[0]['index'],input_data)
        interpreter.invoke()

        # Retrieve detection results
        boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
        scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
        #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

        objects_count=0 #instantiate detected object counts

        # Loop over all detections and draw detection box if confidence is above minimum threshold
        for i in range(len(scores)):
            if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):

                # Draw label
                object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                if(object_name == 'car'):
                    objects_count = objects_count + 1 #get the count of cars detected in the image

        objects_list[image_path] = objects_count
    return(objects_list)