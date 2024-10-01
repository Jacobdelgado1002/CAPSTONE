import numpy as np
from flask import Flask, request, render_template
import tensorflow as tf

app = Flask(__name__)

# load model
model = tf.keras.models.load_model("../../best_model/mobilenetv2_best_f1score_fold_1.h5")

@app.route('/')
def landing():
    return render_template('landing.html')

if __name__ == "__main__":
    app.run(debug=True)