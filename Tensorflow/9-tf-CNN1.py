import tensorflow as tf
from tensorflow.contrib import learn
from tensorflow.contrib import layers
from tensorflow.contrib import losses
from tensorflow.examples.tutorials.mnist import input_data
import pandas as pd
import numpy as np
from sklearn import metrics
import os

os.chdir("//home//tensorflow//")
tf.logging.set_verbosity(tf.logging.INFO)

# read digit images of 28 x 28 = 784 pixels size
# target is image value in [0,9] range; one-hot encoded to 10 columns
mnist = input_data.read_data_sets('MNIST_data', one_hot=True)

X_train = mnist.train.images
y_train = mnist.train.labels

X_validation = mnist.validation.images
y_validation = mnist.validation.labels

X_test = mnist.test.images
y_test = mnist.test.labels

# Hidden layers generally use sigmoid perceptrons
# Output layer uses softmax for overall interpretability of all the 10 outputs
def model_function(features, targets, mode):
    # input layer
    # Reshape features to 4-D tensor (55000x28x28x1)
    # MNIST images are 28x28 pixels
    # batch size corresponds to number of images: -1 represents ' compute the # images automatically (55000)'
    # +1 represents the # channels. Here #channels =1 since grey image. For color image, #channels=3
    input_layer = tf.reshape(features, [-1, 28,28,1])
    
    # Computes 32 features using a 5x5 filter
    # Padding is added to preserve width
    # Input Tensor Shape: [batch_size,28,28,1]
    # Output Tensor Shape: [batch_size,28,28,32]
    conv1 = layers.conv2d(inputs= input_layer,
                          num_outputs=32,
                          kernel_size=[5,5],
                          stride=1,
                          padding="SAME",
                          activation_fn=tf.nn.relu)
    # Pooling layer 1
    # Pooling layer ith a 2x2 filter and stride 2
    # Input shape: [batch_size,28,28,32]
    # Output shape: [batch_size,14,14,32]
    pool1 = layers.max_pool2d(inputs=conv1,
                              kernel_size=[2,2],
                              stride=2)
    
    # Flatten the pool1 to feed to the 1st layer of fully connected layers
    # Input size: [batch_size,14,14,32]
    # Output size: [batch_size, 14x14x32]
    pool1_flat = tf.reshape(tensor=pool1, shape=[-1,14*14*32])
    
    # Connected layers with 100, 20 neurons
    # Input shape: [batch_size, 14x14x32]
    # Output shape: [batch_size, 10]
    fclayers = layers.stack(pool1_flat,layers.fully_connected,[100,20], 
                            activation_fn=tf.nn.relu)
                            #weights_initializer=layers.xavier_initializer(uniform=True, seed=196))
                     
    outputs = layers.fully_connected(inputs=fclayers,
                                     num_outputs=10,    # 10 perceptrons in output layer for 10 numbers (0 to 9)
                                     activation_fn=None) # Use "None" as activation function specified in "softmax_cross_entropy" loss
    
     # Calculate loss using cross-entropy error; also use the 'softmax' activation function
    loss = losses.softmax_cross_entropy(outputs, targets)
     
    optimizer = layers.optimize_loss(loss = loss,
                                      global_step = tf.contrib.framework.get_global_step(),
                                      learning_rate = 0.5,
                                      optimizer = "SGD")
     
     # Class of output (i.e., predicted number) corresponds to the perceptron returning the highest fractional value
     # Returning both fractional values and corresponding labels    
    probs = tf.nn.softmax(outputs)
    #return {'Probs:' probs, 'labels:'tf.argmax(probs, 1)}, loss, optimizer
    return {'probs':probs, 'labels':tf.argmax(probs, 1)}, loss, optimizer
    # Applying softmax on top of plain outputs from layer (linear activation function since activation_fn=None) to give results
    
classifier = learn.Estimator(model_fn=model_function, model_dir="//home//tensorflow//Models//CNN-Models//model1")
classifier.fit(x=X_train, y=y_train, steps=6000, batch_size=100)

for var in classifier.get_variable_names():
    print var, ": ", classifier.get_variable_value(var).shape, " - ", classifier.get_variable_value(var) 
    

#evaluate the model using validation set
results = classifier.evaluate(x=X_validation, y=y_validation, steps = 1)
for key in sorted(results):
    print "%s:%s" %(key, results[key])
    
# Predict the outcome of test data using model
predictions = classifier.predict(X_test)
metrics.accuracy_score(np.argmax(y_test,1), predictions['labels'])
#0.98029999999999995

    
