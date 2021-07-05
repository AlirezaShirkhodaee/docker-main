import requests
import json
import argparse
import codecs
#client fills this arguments via get request in html or post in terminal
parser = argparse.ArgumentParser()
parser.add_argument('--image', default='pic10.jpeg', type=str)
parser.add_argument('--face_detection', default=False, action='store_true')
parser.add_argument('--output_file', default='output.png', type=str)
parser.add_argument('--server_ip', default='localhost', type=str)
parser.add_argument('--server_port', default=5000, type=int)
args = parser.parse_args()

data = {'image': args.image}
if args.face_detection:
    res = requests.post(f'http://{args.server_ip}:{str(args.server_port)}/face_detection_api', data=json.dumps(data))
    res = json.loads(res.text)
    if res['message'] == 'Image Not Found':
        print('Image not found in the server.')
    elif res['face detection'] == "Error In Face Detection":
        print("There is an error in face detection.")
    else:
        face_dict = json.loads(res['face detection'])
        print(f"Number of face detected is {face_dict['faces_count']}")
else:
    res = requests.post(f'http://{args.server_ip}:{str(args.server_port)}/image_processing_api', data=json.dumps(data))
    if res.text == 'Image Not Found':
        print('Image not found in the server.')
    else:
        res = res.content
        with open(args.output_file, "wb") as f:
            f.write(codecs.decode(res, 'base64'))
            print(f'Image saved as {args.output_file}')
