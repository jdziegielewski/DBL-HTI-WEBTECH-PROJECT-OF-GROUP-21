# Largely boiler plate code from flask documentation, slightly edited to make it work.
import os, shutil
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

shutil.rmtree('/uploads') #remove any existing files before running, no easy option for this in os module
if not os.path.isdir('/uploads'):
    os.mkdir('/uploads') # make upload directory

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['./uploads'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            #flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            #flash('No selected file') <- causes error when pressing upload without selecting file
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['./uploads'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))

    uploaded_files = os.listdir('/uploads')
    return render_template('upload.html', files=uploaded_files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return render_template('uploaded.html', filename=filename)