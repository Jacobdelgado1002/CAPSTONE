import numpy as np
from PIL import Image
from flask import Flask, request, redirect, url_for, render_template
import tensorflow as tf

app = Flask(__name__)

gpu = tf.config.list_physical_devices('GPU')[0]
tf.config.experimental.set_memory_growth(gpu, True)

# Load Models
models = {
    "Original": tf.saved_model.load('../../best_model/model1/best_f1score_fold'),
    "FP32": tf.saved_model.load('../../tensorRT_model/fp32'),
    "FP16": tf.saved_model.load('../../tensorRT_model/fp16'),
    "INT8": tf.saved_model.load('../../tensorRT_model/int8')
}

# Warm up models:
img = Image.open('static/uploads/uploaded_image.png').convert("RGB").resize((224, 224)) # Used image saved locally as input
img = np.array(img)
img = img / 255.0  # Normalize pixel values  
img = np.expand_dims(img, axis=0)
img_to_tensor = tf.convert_to_tensor(img, dtype=tf.float32)
for key in models:
    model = models.get(key)
    print(model)
    infer = model.signatures["serving_default"]
    infer(img_to_tensor)

# Establish Labels
classified_as = ['Monkeypox', 'Not Monkeypox']


# Landing route of the application
@app.route('/')
def landing():
    return render_template('landing.html')


# Upload success route of the application
# Receives result, probability and model as parameters
@app.route('/upload/success')
def upload_success():
    result = request.args.get('result')  
    probability = request.args.get('probability')
    model_used = request.args.get('model')

    return render_template('upload-success.html', result = result, probability = probability, modelName = model_used)


# Upload failed route of the application
# Called when an error occurs within upload to avoid crashing the page
@app.route('/upload/failed')
def upload_failed():
    return render_template('upload-failed.html')

# Upload route, runs when pressing the upload button from landing page
@app.route('/upload', methods=['POST'])
def upload():
    wrongFile = False

    selected_model_key = request.form.get('model', 'Original')  # Default to 'Original' if not provided
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

            # Run prediction
            print(f"\nRunning output...\n")
            infer = model.signatures["serving_default"]
            output = infer(img_to_tensor)

            print("\nSetting values...\n")

            prediction_logits = output["output_0"].numpy()
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
        
        # Print error to identify easier what the cause was
        print(f"Unexpected error: {e}")
        return redirect(url_for('upload_failed'))
        

if __name__ == "__main__":
    app.run(debug=True)