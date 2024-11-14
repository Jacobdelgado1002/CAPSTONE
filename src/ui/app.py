import numpy as np
import io
import base64
from PIL import Image
from flask import Flask, request, redirect, url_for, render_template
import tensorflow as tf

app = Flask(__name__)


# Load the SavedModel using TFSMLayer, treating it as a Keras layer
# model_layer = tf.keras.layers.TFSMLayer('../../best_model/model1/best_f1score_fold', call_endpoint='serving_default')
# model_layer = tf.keras.layers.TFSMLayer('../../tensorRT_model/test', call_endpoint='serving_default')

# Wrap the TFSMLayer in a Sequential model for inference
# model = tf.keras.Sequential([model_layer])

#Find how to have them warmed up, the optimized ones take a while to give prediction
models = {
    "Original": tf.saved_model.load('../../best_model/model1/best_f1score_fold'),
    "FP32": tf.saved_model.load('../../tensorRT_model/fp32'),
    "FP16": tf.saved_model.load('../../tensorRT_model/fp16'),
    "INT8": tf.saved_model.load('../../tensorRT_model/int8')
}




# Establish Labels
classified_as = ['Monkeypox', 'Not Monkeypox']


@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/upload/success')
def upload_success():
    result = request.args.get('result')  
    probability = request.args.get('probability')
    model_used = request.args.get('model')

    return render_template('upload-success.html', result = result, probability = probability, modelName = model_used)


@app.route('/upload/failed')
def upload_failed():
    return render_template('upload-failed.html')


@app.route('/upload', methods=['POST'])
def upload():
    wrongFile = False
    selected_model_key = request.form.get('model', 'Original')  # Default to 'Original' if not provided

    # Check if the selected model exists in the dictionary
    model = models.get(selected_model_key)

    try: 
        # some error handling
        if 'file' not in request.files:
            wrongFile = True

        file = request.files['file']
        
        if file.filename == '':
            wrongFile = True
        
        if file:
            print("\nResizing image...\n")

            # Convert file to image and preprocess it
            img = Image.open(file.stream).convert("RGB").resize((224, 224))

            # Save the image with a fixed name directly
            img.save('static/uploads/uploaded_image.png')


            # Preparing img for model input
            img = np.array(img)
            img = img / 255.0  # Normalize pixel values  

            # Add batch dimension (1, 224, 224, 3)
            img = np.expand_dims(img, axis=0)

            print("\nConverting image to tensor...\n")
            img_to_tensor = tf.convert_to_tensor(img, dtype=tf.float32)

            # output = model.signatures["serving_default"](img_to_tensor)
            print(f"\nRunning output...\n")
            # Run prediction
            infer = model.signatures["serving_default"]
            output = infer(img_to_tensor)

            # for key, value in output.items():
            #     output = value.item()

            print("\nSetting values...\n")

            prediction_logits = output["output_0"].numpy()

            # Monkeypox = 0 and Other = 1
            # classes = np.argmax(output, axis = 1)
            # print(f'Classes: {classes}')

            # Probability for the result
            # score = tf.nn.sigmoid(output)
            score = tf.nn.sigmoid(prediction_logits)

            # Only returns the chance of it NOT being monkeypox
            print("\nScore:", score)

            # Classify prediction and score
            probability = score.numpy()
            percentage_value = round(score.numpy().item() * 100, 2)
            predicted_classes = (probability > 0.5).astype(int)
            print(f'\nProbability: {percentage_value}\nPredicted classes {predicted_classes}\n')
            
            # its monkeypox
            if percentage_value < 50:
                class_ = classified_as[0]
                percentage_value = 100 - percentage_value
            else:
                class_ = classified_as[1]

            # Redirect to success page if model was able to process it correctly
            return redirect(url_for('upload_success', result=class_, probability=percentage_value, model=selected_model_key))
        
    except Exception as e:
        if(wrongFile): 
            print('Wrong file, maybe add as a notification and send back to landing')
            return redirect(url_for('landing'))
        
        print(f"Unexpected error: {e}")
        return redirect(url_for('upload_failed'))
        

if __name__ == "__main__":
    app.run(debug=True)