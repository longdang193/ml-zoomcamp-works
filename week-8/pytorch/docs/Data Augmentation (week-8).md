---
aliases: []
status:
time: 2025-11-30-17-00-36
tags:
  - machine-learning/convolutional-neural-networks
TARGET DECK:
---

Data augmentation is a powerful technique used in deep learning for image classification. It serves as a key form of regularization and helps improve model performance by generating additional training examples through programmatic transformations of existing images.

## Rationale for Data Augmentation

Data augmentation addresses the challenges of limited data and overfitting.

* **Improving Model Quality:** Increasing the size of the dataset is one of the most effective ways to improve model performance. When collecting new data is difficult, augmentation provides a practical alternative by creating new examples from existing images.
* **Regularization:** By presenting the model with varied versions of the same image, augmentation reduces the chance of memorization and lowers the risk of overfitting—similar in purpose to techniques like Dropout.
* **Increasing Robustness:** The model becomes less sensitive to irrelevant details such as exact alignment, lighting conditions, or image positioning, improving its ability to generalize.

## Common Image Transformations (Augmentations)

Augmentations work by applying transformations that slightly alter the original image while preserving its label. Multiple transformations may be applied together to produce extensive variation.

| Transformation | Description | Example / Effect |
| ------------------- | --------------------------------------------------- | -------------------------------------------------------------------------- |
| **Flipping** | Mirrors the image horizontally or vertically. | Horizontal flips are common for clothing; vertical flips can also be used. |
| **Rotation** | Rotates the image by a specified range of degrees. | Random rotation between $-30$ and $30$ degrees. |
| **Shifting** | Moves the image horizontally or vertically. | Shifting by values between $-30$ and $30$ pixels. |
| **Shear** | Skews the image along one axis, altering its shape. | Shearing between $-10$ and $10$ pixels. |
| **Zooming** | Scales the image in or out. | Zoom factor between $0.8$ and $1.2$ ($1 \pm 0.2$). |
| **Random Cropping** | Takes a random crop to vary image composition. | Useful after rotating or shifting pants, shirts, etc. |

These transformations produce a richer and more varied training dataset.

## Implementation and Configuration in Keras

Keras uses the **`ImageDataGenerator`** to perform augmentation efficiently.

### A. Data Augmentation Parameters

A generator can be configured with numerous augmentation options, such as:

* `rotation_range=30` — Rotate between $-30$ and $30$ degrees
* `width_shift_range=30` — Horizontal shift between $-30$ and $30$ pixels
* `height_shift_range=30` — Vertical shift between $-30$ and $30$ pixels
* `shear_range=10` — Shear by $-10$ to $10$ pixels
* `zoom_range=0.2` — Zoom between $0.8$ and $1.2$
* `horizontalFlip=True` — Random horizontal flip
* `verticalFlip=False` — No vertical flip

These settings produce new image variations on the fly during training.

### B. Applying Augmentation to Training Data Only

Data augmentation must be applied **only to the training set**.

* **Training Data:** Augmented to increase variability and reduce overfitting.
* **Validation Data:** Must remain unchanged to ensure **consistent and fair evaluation** of model performance.

Applying augmentation to validation images would hinder accurate comparisons between different models or experiments.

## Impact on Performance

Data augmentation improves model quality but also affects the training process.

* **Training Time:** Because each epoch sees altered versions of the same images, the model takes longer to learn. More epochs are typically required.
* **Accuracy Improvement:** In the referenced classification project, augmentation improved performance from $84\%$ to $85\%$ for small images. When combined with larger images ($299 \times 299$), validation accuracy rose to approximately $89\%$.

Data augmentation remains one of the most effective techniques for improving robustness and reducing overfitting in image classification models.
