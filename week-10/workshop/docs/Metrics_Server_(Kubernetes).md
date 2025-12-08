# Metrics Server (Kubernetes)


## What is Metrics Server?

 is a cluster-wide aggregator of resource usage data:

* CPU usage of pods
* Memory usage of pods
* Node resource usage

It is required for:

* `kubectl top nodes`
* `kubectl top pods`
* Horizontal Pod Autoscaler (HPA)

## The "Task Manager" of Kubernetes

Think of Metrics Server as the central dashboard that constantly polls every worker node to check how much energy (CPU/RAM) is being used.

```text
       [ YOUR COMMAND ]                       [ THE AUTOMATION ]
      "kubectl top pods"                  (Horizontal Pod Autoscaler)
              |                                       |
              | 1. "How busy are things?"             | 1. "Is CPU > 80%?"
              v                                       v
+-----------------------------------------------------------------------+
|                         METRICS SERVER                                |
|                  (The Cluster Aggregator)                             |
|            "I collect usage stats every 60s"                          |
+------------------------------+----------------------------------------+
                               ^
                               | 2. Polls Usage Data (Metrics)
                               |
            +------------------+------------------+
            |                                     |
            v                                     v
+-----------------------+               +-----------------------+
|       NODE 1          |               |       NODE 2          |
|  (cAdvisor / Kubelet) |               |  (cAdvisor / Kubelet) |
|                       |               |                       |
|   [ Pod A: 10% CPU ]  |               |   [ Pod C: 90% CPU ]  |
|   [ Pod B: 200MB RAM] |               |   [ Pod D: 50MB RAM]  |
+-----------------------+               +-----------------------+
```

## The Data Flow Loop

This diagram shows how the data moves from the actual container all the way up to the autoscaler.

```text
      STEP 4: ACTION
      (Scaling Decision)
            |
            v
  +---------------------+
  | Horizontal Pod      |  <-- "Oh, Pod C is melting (90%).
  | Autoscaler (HPA)    |       I need to add another replica!"
  +---------+-----------+
            ^
            | STEP 3: READ
            | (HPA checks Metrics Server)
            |
  +---------+-----------+
  |    Metrics Server   |  <-- "Here is the latest report."
  +---------+-----------+
            ^
            | STEP 2: AGGREGATE
            | (Collects data from all nodes)
            |
  +---------+-----------+
  |       Kubelet       |  <-- "Reporting from Node 2..."
  +---------+-----------+
            ^
            | STEP 1: MEASURE
            | (cAdvisor watches the container)
            |
      [ Container ]
      (Running App)
```
