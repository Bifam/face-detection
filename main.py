# Project: Face Detection System

import requests
from train_model import train_model
from extract_embeddings import extract_data
from detector_thread import Camera
from flask import Flask, render_template, Response, request
import cv2
import numpy
import json

# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# @app.route('/')
# @app.route('/stream_video')
# def index():
#     monitor = request.args.get('id')
#     return render_template('index.html', monitor=monitor)


# def gen(camera, monitor):
#     while True:
#         frame = camera.get_frame(monitor)
#         if frame is not None:
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# @app.route('/video_feed/<int:id>')
# def video_feed(id):
#     resp = Response(gen(Camera(), id),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')
#     resp.headers['Access-Control-Allow-Origin'] = '*'
#     return resp


@app.route('/view_json', methods=['POST'])
def view_json():
    response_data = {}
    response_data['detection'] = []
    # validate request data
    if 'id' not in request.form:
        resp = Response(json.dumps(response_data))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    monitor = request.form['id']
    detected_data = Camera().get_json(monitor)
    # get list of targeted persons
    target_person = []
    if 'targets' in request.form:
        target_person = request.form['targets']
    # if there is no target, so track all persons
    if len(target_person) <= 0:
        resp = Response(json.dumps(detected_data))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp    
    # if there are some detected data
    if 'detection' in detected_data and len(detected_data['detection']) > 0:
        for data in detected_data['detection']:
            # if detected data in in targeted persons
            if data['name'] in target_person:
                response_data['detection'].append(data)

    resp = Response(json.dumps(response_data))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/do_training', methods=['GET'])
def do_training():
    confidence = 0.5
    if 'confidence' in request.args:
        confidence = request.args.get('confidence')
    extract_data(confidence)
    train_model()
    return Response(json.dumps({'result': 'ok'}))


@app.route('/change_stream_url', methods=['POST'])
def change_stream_url():
    if 'monitor_id' not in request.get_json():
        return Response(json.dumps({'result': 'ng'}))

    stream_url = ''
    monitor = request.get_json()['monitor_id']
    if ('stream_url' in request.get_json()):
        stream_url = request.get_json()['stream_url']

    Camera().change_stream_url(monitor, stream_url)
    return Response(json.dumps({'result': 'ok'}))


@app.route('/valid_image', methods=['POST', 'PUT'])
def confirm_image():
    response_data = {}
    response_data['detection'] = []
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return Response(json.dumps(response_data))
        file = request.files['file']
        # check if file name is empty
        if file.filename == '':
            return Response(json.dumps(response_data))

        # check file validate
        # if file and allowed_file(file.filename):
        if file:
            filestr = request.files['file'].read()
            # convert string data to numpy array
            npimg = numpy.fromstring(filestr, numpy.uint8)
            # convert numpy array to image
            img = cv2.imdecode(npimg, cv2.IMREAD_UNCHANGED)
            response = Camera().detect_image(img)
            return Response(json.dumps(response))

    return Response(json.dumps(response_data))

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    #app.run(host='0.0.0.0', port='5000', debug=True)
    app.run(host='0.0.0.0', threaded=True)
    # app.run(host='127.0.0.1', threaded=True)
