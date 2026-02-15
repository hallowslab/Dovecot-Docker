# Performance measurements for common\populate_inbox.py 

## Commit IDs:

### 88e86a6fde262f5d9536458d795071770f9dad3f (rev v0.0.1)
1 - Total messages created: 1200000
    * Total time: 45.42 seconds
    * Throughput: 26419 messages/sec
    * Population took 46 seconds

2 - Total messages created: 1200000
    * Total time: 43.46 seconds
    * Throughput: 27610 messages/sec
    * Population took 44 seconds

3 - Total messages created: 1200000
    * Total time: 44.93 seconds
    * Throughput: 26707 messages/sec
    * Population took 45 seconds

### 2202f0c41f3abf67200f70a0560e80f4c51cb77c (switch from python's  file object to os.open)
1 - Total messages created: 1200000
    * Total time: 41.22 seconds
    * Throughput: 29113 messages/sec
    * Population took 41 seconds

2 - Total messages created: 1200000
    * Total time: 39.74 seconds
    * Throughput: 30194 messages/sec
    * Population took 40 seconds

3 - Total messages created: 1200000
    * Total time: 39.14 seconds
    * Throughput: 30656 messages/sec
    * Population took 39 seconds