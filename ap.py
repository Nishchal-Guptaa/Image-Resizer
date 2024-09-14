from flask import Flask, render_template, request, url_for, send_from_directory
import os
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import cv2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'FOR_THE_GLORY'
app.config['UPLOAD_FOLDER'] = 'static/test'

class ImgInput(FlaskForm):
    file = FileField('Image')
    submit = SubmitField('Upload file')

# Global variables to store file path and URL
file_url = None
file_path = None

@app.route("/", methods = ['POST','GET'])
def index():
    Photo = ImgInput()
    global file_url, file_path
    file_url = None
    file_path = None
    if Photo.validate_on_submit():
        file = Photo.file.data
        filename = secure_filename(file.filename)
         # Save the file to the upload folder
        save_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        file_path = os.path.join(save_folder, filename)
        file.save(file_path)
        file_url = url_for('static', filename = f'test/{filename}')

    return render_template("index.html", form = Photo, file_url = file_url)

@app.route("/edit", methods = ['POST','GET'])
def edit():
    global file_url, file_path
    if file_path == None:
        return "No file Chosen"
    else:
        
        return render_template("edit.html", file_url=file_url)
    
@app.route("/response", methods = ['POST','GET'])
def response():
    new_h = request.form.get("new_height")
    new_w = request.form.get("new_width")

    if not new_h or not new_w:
        return "Invalid dimensions"

    new_h = int(new_h)
    new_w = int(new_w)

    global file_url, file_path
    img = cv2.imread(file_path)
    height = img.shape[0]
    width = img.shape[1]

    height = new_h
    width = new_w

    resized_img = cv2.resize(img,(width, height))

    # Save the resized image
    resized_filename = f"resized_{os.path.basename(file_path)}"
    resized_file_path = os.path.join(os.path.dirname(file_path), resized_filename)
    cv2.imwrite(resized_file_path, resized_img)

    # Generate the URL for the resized image
    resized_file_url = url_for('static', filename=f'test/{resized_filename}')
    resized_file_url = url_for('download_file', filename=resized_filename)

    return render_template("edit.html", file_url=file_url, resized_file_url=resized_file_url, width=new_w, height=new_h)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    

if __name__ == '__main__':
    app.run()