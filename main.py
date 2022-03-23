from email.policy import default
from nis import match
import cv2
from flask import Flask, flash, request, redirect, url_for, render_template
import os
from werkzeug.utils import secure_filename

PEOPLE_FOLDER = os.path.join('static', 'people_photo')
UPLOAD_FOLDER = r'static/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
app = Flask(__name__)
app.secret_key = "cairocoders-ednalan"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def checkInput(ops):
    select = 0
    customize = 0
    if (ops["flip"] or ops["rotate"] or ops["resize"] or ops["grayscale"] or 
        ops["thumbnail"] or ops["rotate_right"] or ops["rotate_left"]):
        select = 1
    if ops["customization"]:
        customize = 1
    return select+customize, select

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def access_img(filename):
    path = r'static/' + filename
    src = cv2.imread(path)
    return src

def impl_customization(ops):
    ops_done = []
    for pair in ops:
        op = pair.split(" ")[0]
        value = pair.split(" ")[1]
        if (op == "flip" or op == "rotate" or op == "resize" or op == "grayscale" or 
            op == "thumbnail" or op == "rotate_right" or op == "rotate_left"):
                ops_done.append((op, value))
        else:
            return "wrong"
    return ops_done


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/perform', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']

    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print('upload_image filename: ' + filename)       
        isProcess = False
        select = 0

        sum, select = checkInput(request.form)

        if sum == 2:
            return "Choose either the slected or the custmized."
        
        ops_done = []

        for op in request.form:
            match op:
                case "customization":
                    if not request.form[op]:
                        continue
                    ops_done = impl_customization(request.form["customization"].split(', '))
                    if ops_done == "wrong":
                        return "Invalid customized operations."
                case _:
                    if not request.form[op]:
                        continue
                    ops_done.append((op, request.form[op]))
                    continue


        for first, second in ops_done:
            match first:
                case "flip":
                    if select == 1 and not request.form[first]:
                        continue
                    try:
                        flip = int(second)
                    except:
                        return "The flip operation only accepts 0 or 1 as a parameter."

                    if flip == 0 or flip == 1:
                        src = access_img(filename)
                        file = cv2.flip(src, flip)
                        cv2.imwrite(UPLOAD_FOLDER + filename, file)
                        print("Apply flip to image!")
                        isProcess = True
                    else:
                        return "The flip operation only accepts 0 or 1 as a parameter."                  
                    continue

                case "rotate":
                    if select == 1 and not request.form[first]:
                        continue                   
                    try:
                        rotate = int(second)
                    except:
                        return "The rotate operation only accepts integer."

                    src = access_img(filename)
                    (h, w) = src.shape[:2]
                    (cX, cY) = (w // 2, h // 2)
                    img = cv2.getRotationMatrix2D((cX, cY), rotate, 1.0)
                    file = cv2.warpAffine(src, img, (w, h))
                    cv2.imwrite(UPLOAD_FOLDER + filename, file)
                    print("Apply rotate to image!")
                    isProcess = True
                    continue

                case "resize":
                    if select == 1 and not request.form[first]:
                        continue
                    try:
                        resize = int(second)
                    except:
                        return "The resize operation only accepts integer."

                    src = access_img(filename)
                    width = int(src.shape[1] * resize / 100)
                    height = int(src.shape[0] * resize / 100)
                    dim = (width, height)
                    file = cv2.resize(src, dim, interpolation=cv2.INTER_AREA)
                    cv2.imwrite(UPLOAD_FOLDER + filename, file)
                    print("Apply resize to image!")
                    isProcess = True
                    continue

                case "grayscale":
                    if select == 1 and not request.form[first]:
                        continue
                    try:
                        grayscale = int(second)
                    except:
                        return "The grayscale operation only accepts 0 or 1 as a parameter."

                    if grayscale == 1:
                        src = access_img(filename)
                        file = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
                        cv2.imwrite(UPLOAD_FOLDER + filename, file)
                        print("Apply grayscale to image!")
                        isProcess = True
                    elif grayscale == 0:
                        continue
                    else:
                        return "The grayscale operation only accepts 0 or 1 as a parameter."
                    continue

                case "thumbnail":
                    if select == 1 and not request.form[first]:
                        continue
                    try:
                        thumbnail = int(second)
                    except:
                        return "The thumbnail operation only accepts 0 or 1 as a parameter."

                    if thumbnail == 1:
                        src = access_img(filename)
                        width = int(src.shape[1] * 0.1)
                        height = int(src.shape[0] * 0.1)
                        dim = (width, height)
                        file = cv2.resize(src, dim, interpolation = cv2.INTER_AREA)
                        cv2.imwrite(UPLOAD_FOLDER + filename, file)
                        print("Apply grayscale to image!")
                        isProcess = True
                    elif thumbnail == 0:
                        continue
                    else:
                        return "The thumbnail operation only accepts 0 or 1 as a parameter."
                    continue

                case "rotate_left":
                    if select == 1 and not request.form[first]:
                        continue
                    if not request.form[op]:
                        continue
                    try:
                        rotate_left = int(second)
                    except:
                        return "The rotate_left operation only accepts 1, 2, or 3 as a parameter."

                    if rotate_left == 1 or rotate_left == 2 or rotate_left == 3:
                        for _ in range(rotate_left):
                            src = access_img(filename)
                            file = cv2.rotate(src, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
                            cv2.imwrite(UPLOAD_FOLDER + filename, file)
                        print("Apply rotate_left to image!")
                        isProcess = True
                    else:
                        return "The rotate_left operation only accepts 1, 2, or 3 as a parameter."
                    continue

                case "rotate_right":
                    if select == 1 and not request.form[first]:
                        continue
                    try:
                        rotate_right = int(second)
                    except:
                        return "The rotate_right operation only accepts 1, 2, or 3 as a parameter."

                    if rotate_right == 1 or rotate_right == 2 or rotate_right == 3:
                        for _ in range(rotate_right):
                            src = access_img(filename)
                            file = cv2.rotate(src, cv2.cv2.ROTATE_90_CLOCKWISE)
                            cv2.imwrite(UPLOAD_FOLDER + filename, file)
                        print("Apply rotate_right to image!")
                        isProcess = True
                    else:
                        return "The rotate_right operation only accepts 1, 2, or 3 as a parameter."               
                    continue
        if isProcess:
            cv2.imwrite(UPLOAD_FOLDER+filename, file)
        flash('Image successfully uploaded and displayed below')
        return render_template('index.html', filename=filename)
    else:
        return "Allowed image types are - png, jpg, jpeg"

@app.route('/display/<filename>')  
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename=filename), code=301)


if __name__ == "__main__":
    app.run()
