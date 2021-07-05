from flask import Flask, render_template, request
import json
import base64
from glob import glob
import os
import cv2

#setting up server_ip and port_ip and volume location
server_ip = os.getenv("server_ip", default='0.0.0.0')
server_port = int(os.getenv("server_port", default='5000'))
volume = os.getenv("volume_address", default='Volume')
#import an opencv model for face recognition
cascPath = os.getenv("cascade", default='haarcascade_frontalface_default.xml')
debug = int(os.getenv("dubug", default='0'))

faceCascade = cv2.CascadeClassifier(cascPath)

#listing all images in volume address
image_formats = ['.png', '.jpg', '.jpeg', '.gif']
image_list = []
for image_format in image_formats:
    image_list.extend(glob(volume + os.sep + '*' + image_format))

app = Flask(__name__)
app.config["DEBUG"] = (debug == 1)

#function to get serialof image
def serialize_image(image):
    with open(image, "rb") as imageFile:
        str = base64.b64encode(imageFile.read())
    return str

# this function gets name of pic and returns a dictionary contains faces
def face_detection(image):
    try:
        face_dict = os.popen(f'curl -X POST -F "file=@{image}" http://localhost:8080/').read()
    except:
        face_dict = "Error In Face Detection"
    return face_dict


def face_detector_tool(image):
    image_address = volume + os.sep + image
    #load image
    img = cv2.imread(image_address)
    #gray scale it
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #find faces in image

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    filename = image[0:image.rfind('.')] + "_face_detected" + image[image.rfind('.'):]
    cv2.imwrite(volume + os.sep + filename, img)
    image_list.append(volume + os.sep + filename)
    return filename

#runs when client make a request to /image_processing
@app.route('/image_processing', methods=['GET', 'POST'])
def home():
    post_request = False
    image_exists = False
    image = ''
    if request.method == 'POST':
        post_request = True
        FD_option = request.form['FaceDetection']
        if FD_option == 'yes':
            FD_option = True
        else:
            FD_option = False
        image = request.form.get('image')
        image_address = volume + os.sep + image
        if image_address in image_list:
            image_exists = True
            if FD_option:
                image = face_detector_tool(image)
        else:
            image_exists = False
    return render_template("index.html", post_request=post_request, image_exists=image_exists, image=image)


@app.route('/image_processing_api', methods=['POST'])
def rest_api_image_processing():
    data = json.loads(request.data)
    image = volume + os.sep + data['image']
    if image in image_list:
        response = serialize_image(image)
    else:
        response = 'Image Not Found'
    return response


@app.route('/face_detection_api', methods=['POST'])
def rest_api_face_detection():
    data = json.loads(request.data)
    response = {}
    image = volume + os.sep + data['image']
    if image in image_list:
        response['message'] = 'Image Found'
        response['face detection'] = face_detection(image)
    else:
        response['message'] = 'Image Not Found'
        response['face detection'] = None
    return json.dumps(response)

# run this program on server_ip and server_port
app.run(port=server_port, host=server_ip)
