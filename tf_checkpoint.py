# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 12:48:02 2021

tf.train.checkpoint
https://www.tensorflow.org/api_docs/python/tf/train/Checkpoint

Training checkpoints
https://www.tensorflow.org/guide/checkpoint

@author: James Ang
"""

import tensorflow as tf
from tensorflow.keras.layers import Dense


class Net(tf.keras.Model):
    """A simple linear model."""
    
    def __init__(self):
        super(Net, self).__init__()
        self.l1 = tf.keras.layers.Dense(5)
    
    def call(self, x):
        return self.l1(x)
    
net = Net()
net.save_weights('tmp/easy_checkpoint')

def toy_dataset():
  inputs = tf.range(10.)[:, None]
  labels = inputs * 5. + tf.range(5.)[None, :]
  return tf.data.Dataset.from_tensor_slices(
    dict(x=inputs, y=labels)).repeat().batch(2)

def train_step(net, example, optimizer):
  """Trains `net` on `example` using `optimizer`."""
  with tf.GradientTape() as tape:
    output = net(example['x'])
    loss = tf.reduce_mean(tf.abs(output - example['y']))
  variables = net.trainable_variables
  gradients = tape.gradient(loss, variables)
  optimizer.apply_gradients(zip(gradients, variables))
  return loss


opt = tf.keras.optimizers.Adam(0.1)
dataset = toy_dataset()
iterator = iter(dataset)
ckpt = tf.train.Checkpoint(step=tf.Variable(1), optimizer=opt, net=net, iterator=iterator)
manager = tf.train.CheckpointManager(ckpt, './tf_ckpts', max_to_keep=3)

def train_and_checkpoint(net, manager):
    
  ckpt.restore(manager.latest_checkpoint)
  
  if manager.latest_checkpoint:
      
    print("Restored from {}".format(manager.latest_checkpoint))
    
  else:
      
    print("Initializing from scratch.")

  for _ in range(50):
      
    example = next(iterator)
    loss = train_step(net, example, opt)
    ckpt.step.assign_add(1)
    
    if int(ckpt.step) % 10 == 0:
        
      save_path = manager.save()
      print("Saved checkpoint for step {}: {}".format(int(ckpt.step), save_path))
      print("loss {:1.2f}".format(loss.numpy()))


train_and_checkpoint(net, manager)


# RESTORE

opt = tf.keras.optimizers.Adam(0.1)
net = Net()
dataset = toy_dataset()
iterator = iter(dataset)
ckpt = tf.train.Checkpoint(step=tf.Variable(1), optimizer=opt, net=net, iterator=iterator)
manager = tf.train.CheckpointManager(ckpt, './tf_ckpts', max_to_keep=3)

train_and_checkpoint(net, manager)

print(manager.checkpoints)  # List the three remaining checkpoints

