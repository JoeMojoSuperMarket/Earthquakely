from flask import Flask, request, render_template, send_from_directory
import os
from PIL import Image, ImageSequence
import imageio
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # Get list of image filenames in the upload directory
    image_files = [file for file in os.listdir(UPLOAD_FOLDER) if file.endswith('.gif')]
    # Sort the files by modified time
    image_files.sort(key=lambda x: os.path.getmtime(os.path.join(UPLOAD_FOLDER, x)), reverse=True)
    # Select the last four "shaken" images
    last_four_images = image_files[:4]
    # Render the template with the images
    return render_template('index.html', images=last_four_images)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'No file part', 400
    file = request.files['image']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        gif_path = create_shaking_gif(filepath)
        return send_from_directory(os.path.dirname(gif_path), os.path.basename(gif_path))


def create_shaking_gif(filepath):
    img = Image.open(filepath)
    frames = []

    # Create frames with the image shifted slightly in random directions
    for _ in range(10):  # Create 10 frames for the GIF
        shifted_img = img.copy()
        x_shift, y_shift = np.random.randint(-5, 6, size=2)
        shifted_img = shifted_img.transform(shifted_img.size, Image.AFFINE, (1, 0, x_shift, 0, 1, y_shift))
        frames.append(shifted_img)

    # Save the frames as a GIF
    gif_path = filepath.rsplit('.', 1)[0] + '_shaking.gif'
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], optimize=False, duration=100, loop=0)

    return gif_path


if __name__ == '__main__':
    app.run(debug=True)
