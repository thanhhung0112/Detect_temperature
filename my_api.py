from flask import Flask, render_template
from flask_cors import CORS, cross_origin
from flask import request
import cv2 as cv
import os
from random import random
import camera
import detect
import get_time

# Initialize back end server
app = Flask(__name__)

# Apply flask cors
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = 'static'

# The Specifications of clock
min_angle = 17
max_angle = 340
min_value = 0
max_value = 150
loop = 8
url = "http://192.168.0.191:8080/shot.jpg" # using ip webcam app in ch play to get the ip of camera

@app.route('/', methods=['POST', 'GET'])
@cross_origin(origin='*')
def detect_temperature():
    global loop
    if request.method == "POST":
        try:
            # using while loop to get the res value which is the real number
            # ignore the cases which only detected the lines or the circle
            while True:
                # image = request.files['file']
                image = camera.get_frame(url, loop)

                # path_to_save = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                # any detected image on the web is saved at this path
                path_to_save = os.path.join(app.config['UPLOAD_FOLDER'], f'test{loop}.png')
                path_result_file = os.path.join(app.config['UPLOAD_FOLDER'], 'result.txt')

                print("Save = ", path_to_save)
                # image.save(path_to_save)

                x, y, r, circle = detect.detect_circle(image)

                res, img = detect.detect_line(image, circle, min_angle, max_angle, min_value, max_value, x, y, r)

                # check the error cases
                if not(isinstance(res, type(None))):
                    break

            cv.imwrite(path_to_save, img)
            time_current = get_time.get_current_time()

            if os.path.isfile(path_result_file) == False:
                with open(path_result_file, 'w') as f:
                    f.write(f'test{loop}.png - Nhiệt độ: {res} - Time: {time_current}\n')
            else:
                with open(path_result_file, 'a') as f:
                    f.write(f'test{loop}.png - Nhiệt độ: {res} - Time: {time_current}\n')

            # loop += 1 # update the loop value to save different detected images (particularly 5 images at 5 corner)

            # return render_template('index.html', user_image=image.filename, rand=str(random()), msg='Success', res=res)
            return render_template('index.html', user_image=f'test{loop}.png', rand=str(random()), msg='Success', res=res)
        except:
            print("something's wrong, fix bug")
            return render_template('index.html', msg='Không nhận diện được nhiệt độ', loop=loop)

    else:
        return render_template('index.html', loop=loop)

# Start backend
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
