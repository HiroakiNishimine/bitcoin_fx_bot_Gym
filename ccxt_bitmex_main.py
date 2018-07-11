# coding=utf-8
import gym_ccxt_bitmex
import numpy as np
import gym
import datetime

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, BatchNormalization
from keras.layers.advanced_activations import LeakyReLU
from keras.optimizers import Adam

from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

# global variables
start_total_XBT = 0.0
step = 0

ENV_NAME = 'ccxt_bitmex-v0'

# Get the environment and extract the number of actions.
env = gym.make(ENV_NAME)
np.random.seed(123)
env.seed(123)
nb_actions = env.action_space.n

# Next, we build a very simple model.
model = Sequential()
model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
model.add(Dense(48))
model.add(LeakyReLU(alpha=0.3))
model.add(BatchNormalization(momentum=0.8))
model.add(Dense(34))
model.add(LeakyReLU(alpha=0.3))
model.add(BatchNormalization(momentum=0.8))
model.add(Dense(17))
model.add(LeakyReLU(alpha=0.3))
model.add(BatchNormalization(momentum=0.8)) 
model.add(Dense(nb_actions))
model.add(Activation('linear'))

model.load_weights(
    'dqn_ccxt_bitmex-v0_weights_2018_7_11_22_46.h5f')

print(model.summary())

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=10,
               target_model_update=1e-2, policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# Okay, now it's time to learn something! We visualize the training here for show, but this
# slows down training quite a lot. You can always safely abort the training prematurely using
# Ctrl + C.
dqn.fit(env, nb_steps=700, visualize=False, verbose=2) # 1step:36sec, 1000step:10hours

# After training is done, we save the final weights.
date = datetime.datetime.now()
dqn.save_weights('dqn_{0}_weights_{1}_{2}_{3}_{4}_{5}.h5f'.format(
    ENV_NAME, date.year, date.month, date.day, date.hour, date.minute), overwrite=False)

dqn.fit(env, nb_steps=3000, visualize=False, verbose=2)

# Finally, evaluate our algorithm for 5 episodes.
# dqn.test(env, nb_episodes=5, visualize=True)
