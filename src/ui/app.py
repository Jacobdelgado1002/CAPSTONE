import numpy as np
from PIL import Image
from flask import Flask, request, redirect, url_for, render_template
import tensorflow as tf
from tensorflow.keras import layers

app = Flask(__name__)

# load model
model = tf.keras.models.load_model("../../best_model/mobilenetv2_best_f1score_fold_2.h5")

# Establish Labels
classified_as = ['Monkeypox', 'Not Monkeypox']

@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/upload/success')
def upload_success():
    result = request.args.get('result')  
    probability = request.args.get('probability')

    return render_template('upload-success.html', result = result, probability = probability)


@app.route('/upload/failed')
def upload_failed():
    return render_template('upload-failed.html')


@app.route('/upload', methods=['POST'])
def upload():
    wrongFile = False

    try: 
        # some error handling
        if 'file' not in request.files:
            wrongFile = True

        file = request.files['file']
        
        if file.filename == '':
            wrongFile = True
        
        if file:
            print("Resizing image...")

            # Convert file to image and preprocess it
            img = Image.open(file.stream).convert("RGB").resize((224, 224))
            img = np.array(img)
            img = img / 255.0  # Normalize pixel values  

            # Add batch dimension (1, 224, 224, 3)
            img = np.expand_dims(img, axis=0)

            print("Converting image to tensor...")
            img_to_tensor = tf.convert_to_tensor(img)

            # Normalization
            # normalization_layer = layers.Rescaling(1./255) 
            # img_to_tensor = normalization_layer(img_to_tensor)  

            print("Running output...")
            # Run prediction
            # Currently, it fails to predict correctly actual images (i.e. an image of my arm with a lunar yeilds 94% monkeypox)
            output = model.predict(img_to_tensor)
            print(output)

            print("Setting values...")
            # Monkeypox = 0 and Other = 1
            classes = np.argmax(output, axis = 1)

            # Probability for the result
            score = tf.nn.sigmoid(output[0])

            # Classify prediction and score
            class_ = classified_as[classes[0]]
            probability = score[classes[0]].numpy()
            percentage_value = round(probability * 100, 2)

            # Redirect to success page if model was able to process it correctly
            return redirect(url_for('upload_success', result=class_, probability=percentage_value))
    except:
        if(wrongFile): 
            print('Wrong file, maybe add as a notification and send back to landing')
            return redirect(url_for('landing'))
        
        return redirect(url_for('upload_failed'))

if __name__ == "__main__":
    app.run(debug=True)