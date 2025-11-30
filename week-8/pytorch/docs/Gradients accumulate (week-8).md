---
aliases: []
status:
time: 2025-11-30-14-21-17
tags:
  - python/pytorch
TARGET DECK:
---

```python
optimizer.zero_grad()
```

It **resets all gradients to zero** before computing new gradients for the next batch.

Without this, PyTorch **adds** new gradients on top of the old ones.

## Why gradients accumulate (with a real example)

### Imagine a model with one parameter

```
weight = 2.0
```

You run two batches through the training loop without zeroing gradients.

## Case 1: Forgetting to zero gradients

```python
optimizer.zero_grad()   # start clean
loss1.backward()        # gradient = 3
optimizer.step()        # updates weight

loss2.backward()        # gradient = 5  (BUT accumulates)
optimizer.step()        # uses gradient = 3 + 5 = 8  ❌
```

PyTorch does this by default:

```
param.grad = param.grad + new_grad
```

So after two batches:

```
Expected gradient: 5
Actual gradient:   8  (wrong!)
```

This leads to:

* bad updates
* exploding weights
* training instability
* poor accuracy

## Case 2: Correct behavior with zero_grad()

```python
optimizer.zero_grad()   # gradient = 0
loss1.backward()        # gradient = 3
optimizer.step()

optimizer.zero_grad()   # reset again!
loss2.backward()        # gradient = 5
optimizer.step()        # uses ONLY 5 (correct)
```

Each batch is independent → gradients are correct.

## Visual analogy

Think of `.grad` as a **bucket that stores gradients**:

```
Batch 1:
grad bucket += 3  → bucket = 3

Batch 2:
grad bucket += 5  → bucket = 8   (wrong!)
```

`zero_grad()` empties the bucket:

```
Before Batch 2:
zero_grad() → bucket = 0
grad bucket += 5 → bucket = 5   (correct)
```

## Final Summary

* PyTorch **accumulates gradients by default**
* `zero_grad()` makes sure each batch starts fresh
* Without it → gradients grow incorrectly → training becomes unstable
* With it → correct gradients → stable learning

This is why the training loop always includes:

```python
optimizer.zero_grad()
```

before:

```python
loss.backward()
```
