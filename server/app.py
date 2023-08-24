from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import cv2
import os
import sys
from tqdm import tqdm
import datetime
import pandas as pd
from algos.detection.simple_blob_detector import detect_blobs
from algos.tracking.tracker_stonesoup import track
import base64

app = Flask(__name__)
cors = CORS(app)


@app.route('/upload', methods=['POST'])
def upload():
    print("Got Here1")
    # print(request.files)
    # if 'files' not in request.files:
    #     print("Got Here2")
    #     return 'No files uploaded.', 400
    print("Got Here2.5")
    uploaded_files = request.files.getlist('files')
    if len(uploaded_files) == 0:
        print("Got Here3")
        return 'No files selected.', 400
    
    print("Got Here4")

    # Secure the folder name to prevent any malicious folder names
    current_time = datetime.datetime.now()
    folder_name = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    os.mkdir(f'uploads/{folder_name}')
    os.mkdir(f'uploads/{folder_name}/images')
    print("New folder created:", folder_name)

    video_processed = False
    folder_processed = False

    for uploaded_file in uploaded_files:
        filename = secure_filename(uploaded_file.filename)
        if filename.lower().endswith(('.mp4', '.avi', '.mov', '.wmv')):
            video_processed = True
            file_path = f'uploads/{folder_name}/{filename}'
            uploaded_file.save(file_path)

        elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            folder_processed = True
            file_path = f'uploads/{folder_name}/images/{filename}'
            uploaded_file.save(file_path)


    if video_processed:
        # Process the video

        print("Extracting images...")
        # extract_frames(f'uploads/{folder_name}/{filename}', f'uploads/{folder_name}/images')
        extract_frames(folder_name, filename)

        print("Detecting aphids in the video...")
        get_detections(folder_name)

        print("Tracking the aphids...")
        track(f'uploads/{folder_name}')

        print("Saving the video...")
        save_video(f'uploads/{folder_name}/tracks', f'uploads/{folder_name}/track_video.mp4')

    if folder_processed:
        # Process the folder of images
        print("Detecting aphids in the images...")
        get_detections(folder_name)

        print("Tracking the aphids...")
        track(f'uploads/{folder_name}')

        print("Saving the video...")
        save_video(f'uploads/{folder_name}/tracks', f'uploads/{folder_name}/track_video.mp4')

    # Encode the processed video as base64
    video_base64 = get_processed_video_as_base64(folder_name)

    response_data = {
        'message': 'File(s) uploaded and processed successfully.',
        'video': video_base64
    }
    ret = jsonify(response_data)
    return ret

def get_processed_video_as_base64(folder_name):
    video_path = f'uploads/{folder_name}/track_video.mp4'
    with open(video_path, 'rb') as file:
        video_data = file.read()

    # Convert video data to base64
    video_base64 = base64.b64encode(video_data).decode('utf-8')
    return video_base64

def get_detections(p):
    l_dir = os.listdir(os.path.join('uploads', p ,'images'))
    dets = pd.DataFrame()
    t = datetime.datetime(year=2, month=2, day=2)
    for idx, f in tqdm(enumerate(l_dir)):
        img_path = os.path.join("uploads", p, 'images', f)
        if (not os.path.isfile(img_path)) or (f[-4:] != '.jpg'):
            continue
        detection_blobs, img_blobs = detect_blobs(img_path)
        det_dict = {}
        X, Y, R = [], [], []
        for detection_blob in detection_blobs:
            X.append(detection_blob.pt[0])
            Y.append(detection_blob.pt[1])
            R.append(detection_blob.size)

        det_dict['x'] = X
        det_dict['y'] = Y
        det_dict['r'] = R
        det_dict['time'] = t + datetime.timedelta(seconds=idx)
        dets = pd.concat([dets, pd.DataFrame.from_records(det_dict)])

    dets.to_csv(os.path.join("uploads", p, 'dets.csv'), index=False)

def extract_frames(folder_name, filename):
    # Open the video file
    video = cv2.VideoCapture(f'uploads/{folder_name}/{filename}')
    frame_count = int(video.get(7))
    i=0
    print(f"number of frames in video: {frame_count}")
    # Read the video frames
    while video.isOpened():        

        # printing("Extracting images", i)
        print(f"extracting frame {i}/{frame_count}", end="\r", flush=True)
        i+=1
        ret, frame = video.read()

        if not ret:
            break

        # Save the frame as an image file
        frame_path = f"uploads/{folder_name}/images/frame_{add_zeros_and_number(len(str(frame_count)),i)}.jpg"
        cv2.imwrite(frame_path, frame)

    # Release the video object and close the file
    video.release()
    cv2.destroyAllWindows()

def save_video(images_folder, video_name):
    images = [img for img in os.listdir(images_folder) if img.endswith(".jpg")]
    frame = cv2.imread(os.path.join(images_folder, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_name, 0, 1, (width,height))

    for image in tqdm(images):
        video.write(cv2.imread(os.path.join(images_folder, image)))

    cv2.destroyAllWindows()
    video.release()

def add_zeros_and_number(num_zeros, number):
    # Convert the number to string format
    number_str = str(number)
    
    # Calculate the number of zeros needed to pad the string
    zeros_needed = max(0, num_zeros - len(number_str))
    
    # Concatenate the zeros and the input number
    result = '0' * zeros_needed + number_str
    
    return result

# def printing(text, i):
#     dots = "." * (i % 4)
#     sys.stdout.write("\033[K")  # Clear the line
#     t = " " * (3-len(dots))
#     t = dots+t
#     print(f"{text}{t}{i}", end="\r", flush=True)

if __name__ == '__main__':
    app.run(debug=True)
