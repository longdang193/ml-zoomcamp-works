---
aliases: []
status:
time: 2025-11-30-12-35-52
tags:
  - "#machine-learning/convolutional-neural-networks"
TARGET DECK:
---

The practice of using pre-trained models provides an efficient alternative to training deep learning models from scratch. Training a Convolutional Neural Network (CNN) on a massive dataset like ImageNet—which contains 14 million images—can take weeks of continuous computation, so leveraging existing models significantly reduces time and resource requirements.

## Fundamentals and Model Selection

* **General-Purpose Models:** Pre-trained networks are usually trained on the large and diverse **ImageNet** dataset. Because they learn to classify 1,000 distinct categories, they serve as general-purpose models capable of recognizing a wide variety of visual patterns.
* **Architecture Choice:** Different architectures offer trade-offs in terms of **accuracy, model size, and number of parameters**.
	* **Xception:** Used in the Keras/TensorFlow implementation of the fashion classification project. It combines strong performance with a relatively compact design.
	* **MobileNet V2:** Used in the PyTorch workshop. It is a particularly small and efficient model while still delivering good accuracy.
* **Model Loading:** In Keras, the framework handles downloading pre-trained architectures automatically (e.g., Xception). In PyTorch, pre-trained models such as MobileNet V2 are accessed through the `torchvision` library. When loading a model for inference, it is typically placed in evaluation mode (e.g., `model.eval()`).

## Image Pre-processing for Input

Before an image is fed into a pre-trained network, it must be transformed to match the model’s expected format.

* **Resizing and Cropping:** Images are resized to the required dimensions, such as $299 \times 299$ or $150 \times 150$. In PyTorch, this may include resizing followed by a **center crop**.
* **Tensor/Array Conversion:** The image is converted into a multi-dimensional array or tensor representing width, height, and color channels.
* **Batch Creation:** Neural networks expect a batch of images, even if only one image is being processed. A single $299 \times 299$ RGB image is therefore expanded into an array shaped $\left(1, 299, 299, 3\right)$.
* **Normalization:** Framework-specific preprocessing functions (such as Keras’s `preprocess_input` or equivalent PyTorch transforms) normalize pixel values, scaling them from the 0–255 integer range to a smaller, model-compatible range (e.g., 0 to 1 or -1 to 1).

## Prediction and Initial Utility

* **Output:** Running an image through a pre-trained network produces an output vector of 1,000 values, each representing the probability that the image belongs to one of the ImageNet classes.
* **Interpretation:** Tools such as Keras’s `decode_prediction` convert these numerical scores into human-readable class labels.
* **Initial Usefulness:** Even though the models are general-purpose, they can often provide predictions that are “close enough.” For instance, identifying pants as “jeans” or “suit” may already satisfy a basic clothing-recognition requirement, eliminating the need for additional training.

## Transfer Learning

For tasks requiring more specific classifications, **transfer learning** allows the pre-trained network to be adapted to the new problem.

1. **Retention of Features:** The convolutional layers—which extract detailed visual features—are kept intact, as they already encode useful representations learned from ImageNet.
2. **Freezing Weights:** The base model’s parameters are frozen (e.g., setting `trainable=False`) to preserve the high-quality, pre-trained filters and prevent them from being modified during further training.
3. **Replacing the Top Layers:** The original classification layers responsible for predicting 1,000 ImageNet classes are removed (e.g., `include_top=False` in Keras).
4. **Custom Classification:** New dense layers are added and trained on top of the frozen base to produce predictions tailored to the new task, such as classifying ten types of clothing. Because the underlying feature extraction is already in place, training these new layers is comparatively straightforward.
