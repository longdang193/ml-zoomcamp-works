---
aliases: []
status:
time: 2025-11-30-15-36-34
tags:
  - mlops
  - machine-learning/convolutional-neural-networks
TARGET DECK:
---

Model checkpointing is an essential technique in deep learning that ensures the best-performing version of a model is preserved during training. Because validation accuracy fluctuates across epochs, the final epoch does not always produce the strongest model. Checkpointing prevents the optimal weights from being overwritten and avoids unnecessary storage of weaker models.

## The Rationale for Checkpointing

During training, validation accuracy tends to rise and fall rather than improve steadily. A model may reach peak performance at an earlier epoch—such as epoch 4 or 6—but degrade afterward as it begins to overfit. If only the final model is saved, these superior intermediate weights would be lost.

Checkpointing solves this by tracking the **best validation accuracy so far** and saving the model’s weights **only when performance improves**. This selective saving conserves disk space and guarantees that the optimal version is retained.

## Keras Implementation Using `ModelCheckpoint`

Keras provides high-level support for checkpointing through the `ModelCheckpoint` callback. The callback evaluates the model after each epoch and conditionally saves it when validation accuracy increases.

### Example: Defining the Checkpoint Callback

```python
from tensorflow.keras.callbacks import ModelCheckpoint

checkpoint = ModelCheckpoint(
    'xception_v1_{epoch:02d}_{val_accuracy:.3f}.h5',
    save_best_only=True,
    monitor='val_accuracy',
    mode='max'
)
```

### Explanation of Key Parameters

* **Filename Template:** `'xception_v1_{epoch:02d}_{val_accuracy:.3f}.h5'` inserts the epoch number and validation accuracy into the saved filename.
* **`save_best_only=True`:** Ensures that only models showing improved validation accuracy are saved.
* **`monitor='val_accuracy'`:** Specifies that validation accuracy determines whether the model should be saved.

### Using the Callback

```python
model.fit(
    train_ds,
    epochs=10,
    validation_data=val_ds,
    callbacks=[checkpoint]
)
```

Keras automatically handles the comparison and saving logic behind the scenes:

* Keras retrieves validation accuracy for each epoch
* Compares it to the best accuracy so far
* Decides whether to save the model
* Saves it using the given filename pattern
* Updates the “best accuracy” record

## PyTorch Implementation (Manual Logic)

In PyTorch, checkpointing is implemented manually inside the training loop. The code tracks the best validation accuracy encountered and saves the model when improvement occurs.

### Example: Saving a Checkpoint

```python
def save_checkpoint(model, epoch, val_accuracy, checkpoint_prefix='mobilenet_v2'):
    """
    Saves model checkpoint with formatted filename.
    """
    checkpoint_path = f'{checkpoint_prefix}_{epoch+1:02d}_{val_accuracy:.3f}.pth'
    torch.save(model.state_dict(), checkpoint_path)
    return checkpoint_path
```

This function generates a filename containing the epoch number and validation accuracy, then saves the model’s state dictionary to disk.

### Example: Full Training Loop with Checkpointing

```python
def train_and_evaluate_with_checkpointing(model, optimizer, train_loader, val_loader, criterion, num_epochs, device):
    """
    Trains and evaluates a model with checkpointing for best validation accuracy.
    """
    best_val_accuracy = 0.0

    for epoch in range(num_epochs):
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, val_acc = evaluate_model(model, val_loader, criterion, device)

        # Checkpoint logic: save only if performance improves
        if val_acc > best_val_accuracy:
            best_val_accuracy = val_acc
            checkpoint_path = save_checkpoint(model, epoch, val_acc)
            print(f'Checkpoint saved: {checkpoint_path}')

        print(f'Epoch {epoch+1}/{num_epochs}')
        print(f'  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}')
        print(f'  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}')
```

### How This Loop Works

1. **Training Phase:** `train_one_epoch` runs a full pass over the training data.
2. **Validation Phase:** `evaluate_model` measures loss and accuracy on the validation set.
3. **Performance Check:** If the current validation accuracy exceeds `best_val_accuracy`, the new best accuracy is recorded and the model is saved.
4. **Output:** Each epoch prints training and validation metrics, and a checkpoint is saved only when performance improves.

### Checkpointing Workflow

```text
================================================================================
                       CHECKPOINTING LOGIC FLOW
================================================================================

[ INITIALIZATION ]
best_val_accuracy = 0.0  <-- Tracks the current "Champion" score
       |
       v
+------------------------------------------------------------------------------+
|  EPOCH LOOP (e.g., Range 1 to 10)                                            |
|                                                                              |
|  1. TRAIN PHASE                                                              |
|     (Model learns patterns...)                                               |
|                                                                              |
|  2. VALIDATION PHASE                                                         |
|     (Model takes a test) -> Returns: val_acc (e.g., 0.85)                    |
|                                                                              |
|  3. THE DECISION GATE (The "If" Statement)                                   |
|                                                                              |
|         Is current val_acc (0.85) > best_val_accuracy (0.0)?                 |
|                   /                                \                         |
|                 YES                                NO                        |
|        (New High Score!)                    (Not good enough)                |
|                  |                                  |                        |
|                  v                                  v                        |
|     +-------------------------+            +------------------+              |
|     |  UPDATE RECORD          |            |  SKIP SAVE       |              |
|     |  best_val_accuracy =    |            |                  |              |
|     |  0.85                   |            |  (Keep going)    |              |
|     +-----------+-------------+            +--------+---------+              |
|                 |                                   |                        |
|                 v                                   |                        |
|     +-------------------------+                     |                        |
|     |  GENERATE FILENAME      |                     |                        |
|     |  "mobilenet_v2..."      |                     |                        |
|     |  + Epoch (02)           |                     |                        |
|     |  + Acc (0.850)          |                     |                        |
|     |  = "..._02_0.850.pth"   |                     |                        |
|     +-----------+-------------+                     |                        |
|                 |                                   |                        |
|                 v                                   |                        |
|     +-------------------------+                     |                        |
|     |  WRITE TO DISK          |                     |                        |
|     |  torch.save(...)        |                     |                        |
|     |  (Saves State Dict)     |                     |                        |
|     +-----------+-------------+                     |                        |
|                 |                                   |                        |
|                 v                                   v                        |
|     +-------------------------------------------------------+                |
|     |                PRINT EPOCH METRICS                    |                |
|     +-------------------------------------------------------+                |
+------------------------------------------------------------------------------+
       |
       v
[ NEXT EPOCH ]
```

**1. The "Champion" Variable**

* **Code:** `best_val_accuracy = 0.0`
* This variable sits *outside* the loop. It remembers the highest score ever achieved. If the model gets worse in later epochs (overfitting), this variable ensures we ignore those "worse" versions.

**2. The Logic Gate**

* **Code:** `if val_acc > best_val_accuracy:`
* This acts as a filter. We only perform the expensive Input/Output (I/O) operation of writing to the hard drive if the model has actually improved.

**3. The Filename Strategy**

* **Code:** `f'{checkpoint_prefix}_{epoch+1:02d}_{val_accuracy:.3f}.pth'`
* This creates a self-documenting filename.
		* `epoch+1:02d`: Adds a leading zero (e.g., `01`, `02`) so files sort correctly in your folder.
		* `val_accuracy:.3f`: Rounds to 3 decimal places (e.g., `0.851`).
* **Result on Disk:**

	```text
	mobilenet_v2_01_0.720.pth  (Epoch 1: Baseline)
	mobilenet_v2_03_0.810.pth  (Epoch 3: Improved)
	mobilenet_v2_07_0.895.pth  (Epoch 7: Best so far)
	```

	- *Note: Epochs 2, 4, 5, and 6 are missing because the model didn't improve during those times.*

**4. What is saved?**

* **Code:** `model.state_dict()`
* We save the *weights* (the learned parameters), not the entire Python object. This is the standard, lightweight way to save PyTorch models.
