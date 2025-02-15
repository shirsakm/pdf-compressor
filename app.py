import uuid
import os
from flask import Flask, flash, request, redirect, render_template, session, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
from compressor import compress_pdf
from cleanup import setup_logging, cleanup_old_files

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER = '/opt/render/project/src/uploads'

app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


logger = setup_logging()
logger.info("Starting cleanup process")
cleanup_old_files(logger)
logger.info("Cleanup completed")


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Generate a unique user ID if it doesn't exist
        if 'user_id' not in session:
            session['user_id'] = str(uuid.uuid4())
        
        # Create user-specific upload folder
        user_upload_dir = os.path.join(
            app.config['UPLOAD_FOLDER'], session['user_id']
        )
        if not os.path.exists(user_upload_dir):
            os.makedirs(user_upload_dir)

        min_size = request.form.get('min_size', type=int)
        max_size = request.form.get('max_size', type=int)

        # Validate sizes
        if not min_size or not max_size:
            flash('Missing size constraints', 'error')
            return redirect(request.url)
        if min_size > max_size:
            flash('Minimum size cannot exceed maximum size', 'error')
            return redirect(request.url)

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(user_upload_dir, filename))
            
            if os.path.getsize(os.path.join(user_upload_dir, filename)) < min_size * 1024:
                flash('File size is less than the minimum size', 'error')

                # Remove the uploaded file
                os.remove(os.path.join(user_upload_dir, filename))

                return redirect(request.url)
            
            compressed_file_name, compressed_size = compress_pdf(
                os.path.join(user_upload_dir, filename),
                min_size=min_size,
                max_size=max_size
            )

            if not (min_size <= compressed_size <= max_size):
                user_upload_dir = os.path.join(
                    app.config['UPLOAD_FOLDER'], session['user_id']
                )

                compressed_path = os.path.join(user_upload_dir, compressed_file_name)
                os.remove(compressed_path)

                return redirect(request.url)

            return redirect(url_for('download_file', name=compressed_file_name))
    return render_template('home.html')

@app.route('/uploads/<name>')
def download_file(name):
    if 'user_id' not in session:
        flash('Unauthorized access')
        return redirect(url_for('upload_file'))

    # Get the user's upload directory
    user_upload_dir = os.path.join(
        app.config['UPLOAD_FOLDER'], session['user_id']
    )

    return send_from_directory(user_upload_dir, name)