---
aliases: []
status:
time: 2025-11-30-15-43-24
tags:
  - machine-learning/convolutional-neural-networks
TARGET DECK:
---

The addition of inner layers is a technique used in transfer learning to increase the complexity and predictive strength of the custom classification head built on top of a pre-trained model. These layers enhance the classifier’s ability to interpret the high-level features extracted by the convolutional base.

## Rationale for Adding Inner Layers

In transfer learning, the pre-trained convolutional layers of models such as Xception or MobileNet V2 are retained because they produce a highly informative **vector representation** of the image. This vector contains the high-level features needed for classification.

* **Learning Complexity:** While a single dense layer can map this vector to the final class predictions, adding an inner dense layer enables the model to ==learn **more complex feature interactions**==. This additional processing can help the network detect finer distinctions within the extracted features.
* **Improving Accuracy:** By incorporating another layer into the decision pathway, the classifier gains additional modeling capacity that can translate into higher accuracy.

## Implementation and Structure

The inner layer is placed between the feature extraction system and the final classification layer.

* **Location:** It sits between the output of the **pooling layer**, which converts the 3D convolutional output into a 1D feature vector, and the **final output layer**, which produces the class scores.
* **Layer Type:** The new layer is a **dense (fully connected)** layer, meaning every input unit is connected to every output unit.
* **Example Structure (Keras):**
	1. The convolutional output is reduced to a vector using a pooling layer.
	2. An inner dense layer is added—for example: `inner = keras.layers.Dense(100, activation='relu')(vector)`
	3. This inner layer feeds into the final output layer, typically sized for the number of target classes.
* **Tuning the Size:** The number of neurons in this inner layer is a **hyperparameter**. Values such as 64, 100, or 512 must be tested to identify which performs best on validation data.

## Activation Function

Inner dense layers require an activation function to enable the network to learn nonlinear relationships.

* **ReLU Activation:** The **ReLU (Rectified Linear Unit)** function is commonly used because it enables efficient gradient flow and supports the training of deep models.
* **Avoiding Sigmoid:** Although sigmoid was used historically, it suffers from the **vanishing gradient problem**, which makes it unsuitable for deep networks. ReLU avoids this issue and is therefore preferred.

## Consequences: Overfitting and Regularization

Adding layers increases the model’s capacity, which also increases the risk of **overfitting**—the tendency to memorize the training data rather than generalize to new examples.

To counter this risk, regularization techniques are applied:

* **Dropout:** A Dropout layer is typically inserted after the inner dense layer.
* **Mechanism:** Dropout works by **randomly disabling a portion of the layer’s weights** during each training step, forcing the model to learn redundantly from multiple pathways.
* **Effectiveness:** This reduces reliance on any single set of neurons and makes the classifier more robust.
* **Performance Result:** In the referenced implementation, adding an inner dense layer combined with Dropout increased validation accuracy from $83\%$ to $84\%$, demonstrating the usefulness of this technique even when gains are modest.
