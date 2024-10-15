import numpy as np
import io
import base64
from PIL import Image
from flask import Flask, request, redirect, url_for, render_template
import tensorflow as tf
from tensorflow.keras import layers

app = Flask(__name__)


# Load the SavedModel using TFSMLayer, treating it as a Keras layer
model_layer = tf.keras.layers.TFSMLayer('../../best_model/model1/best_f1score_fold', call_endpoint='serving_default')

# Wrap the TFSMLayer in a Sequential model for inference
model = tf.keras.Sequential([model_layer])

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

            # Save the image with a fixed name directly
            img.save('static/uploads/uploaded_image.png')


            # Preparing img for model input
            img = np.array(img)
            img = img / 255.0  # Normalize pixel values  

            # Add batch dimension (1, 224, 224, 3)
            img = np.expand_dims(img, axis=0)

            print("Converting image to tensor...")
            img_to_tensor = tf.convert_to_tensor(img)

            print("Running output...")
            # Run prediction
            output = model.predict(img_to_tensor)

            for key, value in output.items():
                output = value.item()

            print("Setting values...")

            # Monkeypox = 0 and Other = 1
            # classes = np.argmax(output, axis = 1)
            # print(f'Classes: {classes}')

            # Probability for the result
            score = tf.nn.sigmoid(output)

            # Only returns the chance of it NOT being monkeypox
            print("Score:", score)

            # Classify prediction and score
            probability = score.numpy()
            percentage_value = round(probability * 100, 2)
            print(f'Probability: {percentage_value}')
            
            # its monkeypox
            if percentage_value < 50:
                class_ = classified_as[0]
                percentage_value = 100 - percentage_value
            else:
                class_ = classified_as[1]

            # Redirect to success page if model was able to process it correctly
            return redirect(url_for('upload_success', result=class_, probability=percentage_value))
    except:
        if(wrongFile): 
            print('Wrong file, maybe add as a notification and send back to landing')
            return redirect(url_for('landing'))
        
        return redirect(url_for('upload_failed')) 

if __name__ == "__main__":
    app.run(debug=True)