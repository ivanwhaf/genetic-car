# genetic-car
Self-learning car using genetic algorithm

![image](https://github.com/ivanwhaf/genetic-car/blob/master/demo.png)

# Usage
Please run *manual version*, do not run *auto version*, it has not been implemented!
## 1. Run program
```bash
$ python genetic_car_manual.py
```
## 2. Select elites manually
After each round, just click the blue cars who have **Best performance**, and their colors would
turn to red, then press `Space` key to enter next loop

## 3. Repeat until cars can finish the track
Just repeat doing **Step 2** and wait for several iterations, there would be some cars can
complete the whole track. Don't stop, keep doing this, until most cars can finish
the race (i.e. the network model has converged)

# Caution
* Please don't forget selecting elites manually (mouse left button) after each round!
* For many reasons, *Genetic_car_auto.py* has not been implemented -.-
* Yellow car is the car that has the longest running distance, it doesn't matter

# Details
* This repo uses genetic algorithm to optimize the neural network. I construct a network with 3
input layers, 5 hidden layers, and 2 output layers using *numpy*.
* Each car agent has three distances from itself to the track boundary (also the network's input)
* The network model has two output vectors which respectively represents *angle* and *speed* of car
* There are many hyper-parameters with my notations at the beginning of the code, you can customize them

# Requirements
```bash
$ pip install -r requirements.txt
```