import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
from compressor import compress_pdf

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')

app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        min_size = request.form.get('min_size', type=int)
        max_size = request.form.get('max_size', type=int)

        # Validate sizes
        if not min_size or not max_size:
            flash('Missing size constraints')
            return redirect(request.url)
        if min_size > max_size:
            flash('Minimum size cannot exceed maximum size')
            return redirect(request.url)

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            compressed_filename = compress_pdf(
                os.path.join(app.config['UPLOAD_FOLDER'], filename),
                min_size=min_size,
                max_size=max_size
            )

            return redirect(url_for('download_file', name=compressed_filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <br>
        <label>Minimum Size (KB):</label>
        <input type="number" name="min_size" required>
        <br>
        <label>Maximum Size (KB):</label>
        <input type="number" name="max_size" required>
        <br>
        <input type=submit value=Upload>
    </form>
    '''


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)