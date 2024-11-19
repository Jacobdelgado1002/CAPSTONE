# CIIC-4151 (Capstone)

This repository contains the "Computer Vision for Real-Time Monkeypox Diagnosis on Embedded Systems" project


# SETUP

Create a virtual environment locally. You can [follow the guide](https://code.visualstudio.com/docs/python/tutorial-flask). Remember to choose the requirements.txt to import all packages related to the repository.

### TO RUN

Open a new terminal with type Command Prompt or Git Bash. It should automatically activate the virtual environment.

CD into the ui folder. To start the flask server locally:

python -m flask run

After successfull start, you should be able to view the page and interact with it in your localhost.

# GUIDE

### Model Compression

The process of compressing the models can be found in tensorRT.ipynb. We use TensorRT to compress our models to FP32, FP16 and INT8. All of them have a similar format of compression where we start by defining the conversion parameters, pass it onto a TensorRT Converter and applying that converter to our original model. In the case of INT8, we use part of our dataset to calibrate the compressed model. Mainly because compressing a model to INT8 can lose significant precision and be improperly scaled compared to its FP32 and FP16 counterparts. Calibrating converts the floating points to integers and maintains a symmetric range of quantized values.

The compression is based on the GPU of the system. For example, if the compression was made on a GeForce RTX 4080, only in a system with this GPU can run those compressed models. In our case that we wanted to deploy the models in a Jetson, we had to compress them in the Jetson to be able to run them.

### Benchmarking

Both Benchmarking notebooks outline the same process and order of operations. We made a notebook specific to the Jetson because it had less RAM and required a slower, step by step approach. 

Similar to compression, we start by splitting the data into batches that will be used for measuring inference and metrics of our models. After defining the functions, we measure the same things for the Original, FP32, FP16 and INT8 models. A high level output is generated to visualize the results and differences among the models. Finally, we plot these values into easy to understand graphs. These graphs show the model sizes, the model throughput comparison, the average inference time between the models and the metrics comparison.

The graphs from the latest run can be found withing the tensorRT_model -> metrics folder.

### Web Application

The web application, located in app.py, loads all four of the models and performs a warm up trial with the latest saved image.

As of 11/19/2024, it has 3 routes:

Landing ('/')
The inital page that's rendered when the app is started. The user can choose an image from their library or take a new one with their camera and upload it. They can also choose which model will make the prediction, the default model is the Original.

Sucessfull Upload('/upload/success')
After a successfull upload and inference, this page renders the image and returns a prediction with the model used. The user can return to the Landing page and repeat the process.

Upload Failed('/upload/failed')
If something breaks after uploading the image, instead of crashing the web application it will render an error page. An error log will also be printed for easier bug identification and fix. The user can return to the Landing page and start the process again.