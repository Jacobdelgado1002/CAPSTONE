import numpy as np
from PIL import Image
from flask import Flask, request, redirect, url_for, render_template
import tensorflow as tf

app = Flask(__name__)

# load model
model = tf.keras.models.load_model("../../best_model/mobilenetv2_best_f1score_fold_1.h5")

@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/upload_success')
def upload_success():
    return render_template('upload-success.html')


@app.route('/upload', methods=['POST'])
def upload():
    # some error handling
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"
    
    if file:
        # Convert file to image
        img = Image.open(file.stream).resize((224, 224))
        img = np.reshape(np.array(img), [224, 224, 3])
        img = img[np.newaxis, ...]

        img_to_tensor = tf.convert_to_tensor(img)

        # Run prediction
        output = model.predict(img_to_tensor)
        # output = model.predict_classes(img_to_tensor)

        print(output)
        print(output[0][0])
        # Redirect to success page if model was able to process it correctly
        return redirect(url_for('upload_success'))

if __name__ == "__main__":
    app.run(debug=True)