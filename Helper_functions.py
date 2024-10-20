# -*- coding: utf-8 -*-
"""Assignment1_essentials.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1l-6V3Si99FFK56rJSA0wJAmuNF7ZIX4r
"""

from itertools import product
import numpy as np
import matplotlib.pyplot as plt

def gen_boolean_functions(n):
    num_of_inputs = 2 ** n  # Number of possible input combinations
    all_inputs = list(product([0, 1], repeat=n))  # All possible input combinations
    num_of_funs = 2**num_of_inputs
    all_funs=[]
    for i in range(num_of_funs):
        binary_output = format(i, f'0{num_of_inputs}b')
        all_funs.append(binary_output)
    all_funs = np.array(all_funs)
    return all_inputs,all_funs

def is_learnable_by_single_perceptron(inputs, output):
    # Adding bias term to the inputs
    inputs_with_bias = np.c_[np.ones(len(inputs)), np.array(inputs)]  #.c_ appends column wise

    # Use a simple perceptron learning algorithm to try to find weights that linearly separate the data
    weights = np.zeros(inputs_with_bias.shape[1])
    learning_rate = 1.0
    for i in range(100):  # Iterative learning, max 100 iterations
        is_learnable=True
        for x, y in zip(inputs_with_bias, output):
            y=int(y)
            activation = np.dot(weights, x)
            prediction = 1 if activation > 0 else 0
            error = y - prediction
            if error != 0:
                weights += learning_rate * error * x
                is_learnable=False
        if is_learnable:
            return True
    return False

# Define the Base Layer
class Layer:
    def __init__(self):
        self.input = None
        self.output = None

# Define the Dense Layer
class Dense(Layer):
    def __init__(self, input_size: int, output_size: int):
        self.weights = np.random.randn(output_size, input_size) #randn generates random number from -0.5 to 0.5
        self.bias = np.random.randn(output_size, 1)

    def forward(self, input):
        self.input = input
        return np.dot(self.weights, self.input) + self.bias

    def backward(self, output_gradient, learning_rate):
        weights_gradient = np.dot(output_gradient, self.input.T)
        input_gradient = np.dot(self.weights.T, output_gradient)
        self.weights -= learning_rate * weights_gradient
        self.bias -= learning_rate * output_gradient
        return input_gradient

# Activation Layer
class Activation(Layer):
    def __init__(self, activation, activation_prime):
        self.activation = activation
        self.activation_prime = activation_prime

    def forward(self, input):
        self.input = input
        return self.activation(self.input)

    def backward(self, output_gradient, learning_rate):
        return np.multiply(output_gradient, self.activation_prime(self.input))

# Common Activation Functions
class Tanh(Activation):
    def __init__(self):
        def tanh(x):
            return np.tanh(x)

        def tanh_prime(x):
            return 1 - np.tanh(x) ** 2

        super().__init__(tanh, tanh_prime)

class Sigmoid(Activation):
    def __init__(self):
        def sigmoid(x):
            return 1 / (1 + np.exp(-x))

        def sigmoid_prime(x):
            s = sigmoid(x)
            return s * (1 - s)

        super().__init__(sigmoid, sigmoid_prime)

# Softmax layer
class Softmax(Layer):
    def forward(self, input):
        tmp = np.exp(input)
        self.output = tmp / np.sum(tmp)
        return self.output

    def backward(self, output_gradient, learning_rate):
        n = np.size(self.output)
        return np.dot((np.identity(n) - self.output.T) * self.output, output_gradient)

# Loss Functions
def mse(y_true, y_pred):
    return np.mean(np.power(y_true - y_pred, 2))

def mse_prime(y_true, y_pred):
    return 2 * (y_pred - y_true) / np.size(y_true)

def binary_cross_entropy(y_true, y_pred):
    return np.mean(-y_true * np.log(y_pred) - (1 - y_true) * np.log(1 - y_pred))

def binary_cross_entropy_prime(y_true, y_pred):
    return ((1 - y_true) / (1 - y_pred) - y_true / y_pred) / np.size(y_true)

# Neural Network Class
class NeuralNetwork:
    def __init__(self):
        self.layers = []

    def add(self, layer):
        self.layers.append(layer)

    def train(self, x_train, y_train, loss, loss_prime, epochs=1000, learning_rate=0.01, verbose=True):
        epochs_array=[]
        error_array=[]
        for e in range(epochs):
            error = 0
            for x, y in zip(x_train.T, y_train.T):
                x = x.reshape(-1, 1)  # Reshape input to column vector
                y = y.reshape(-1, 1)  # Reshape output to column vector

                # Forward pass
                output = self.predict(x)

                # Compute loss
                error += loss(y, output)
                if error<0.0001:
                  break

                # Backward pass
                grad = loss_prime(y, output)
                for layer in reversed(self.layers):
                    grad = layer.backward(grad, learning_rate)

            error /= len(x_train.T)
            if verbose and e % 100 == 0:
                epochs_array.append(e)
                error_array.append(error)
                print(f"{e + 1}/{epochs}, error={error}")
        plt.plot(epochs_array, error_array)
        plt.xlabel('Epochs')
        plt.ylabel('Error')
        plt.title('Error vs Epochs')
        plt.show()
    def predict(self, input):
        output = input
        for layer in self.layers:
            output = layer.forward(output)
        return output

