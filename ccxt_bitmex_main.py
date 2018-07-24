# coding=utf-8
import gym_ccxt_bitmex
import numpy as np
import gym
import datetime
import argparse
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, BatchNormalization
from keras.layers import CuDNNLSTM
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

# パーサーを作る
parser = argparse.ArgumentParser(
    prog='ccxt_bitmex_main',  # プログラム名
    usage='ccxtライブラリを利用して、bitmexで取引を行うDQN学習プログラム',  # プログラムの利用方法
    description='description',  # 引数のヘルプの前に表示
    add_help=True,  # -h/–help オプションの追加
)

# 引数の追加
parser.add_argument('-l', '--lstm', help='select lstm model', default=True)
parser.add_argument('-m', '--mlp', help='select mlp model', default=False)

# 引数を解析する
args = parser.parse_args()

# Next, we build a model.
print('Build model...')
if args.lstm:
    model = Sequential()
    model.add(CuDNNLSTM(30, input_shape=(1,) + env.observation_space.shape))
    model.add(Dense(22))
    model.add(LeakyReLU(alpha=0.3))
    model.add(BatchNormalization(momentum=0.8)) 
    model.add(Dense(nb_actions))
    model.add(Activation('linear'))
    print('load model...')
    model.load_weights(
        '/home/farmhouse/bitmex/bitcoin_fx_bot/weights/dqn_lstm_ccxt_bitmex-v0_weights_2018_7_25_2_23.h5f')
if args.mlp:
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + env.observation_space.shape))
    model.add(Dense(49))    
    model.add(LeakyReLU(alpha=0.3))
    model.add(BatchNormalization(momentum=0.8))
    model.add(Dense(38))
    model.add(LeakyReLU(alpha=0.3))
    model.add(BatchNormalization(momentum=0.8))
    model.add(Dense(24))
    model.add(LeakyReLU(alpha=0.3))
    model.add(BatchNormalization(momentum=0.8)) 
    model.add(Dense(nb_actions))
    model.add(Activation('linear'))

    # print('load model...')
    # model.load_weights(
    #     'dqn_ccxt_bitmex-v0_weights_2018_7_12_7_33.h5f')

print(model.summary())

# Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
# even the metrics!
memory = SequentialMemory(limit=50000, window_length=1)
policy = BoltzmannQPolicy()
dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=40,
               target_model_update=1e-2, policy=policy)
dqn.compile(Adam(lr=1e-3), metrics=['mae'])

# Okay, now it's time to learn something! We visualize the training here for show, but this
# slows down training quite a lot. You can always safely abort the training prematurely using
# Ctrl + C.
print('Fit model...')
dqn.fit(env, nb_steps=10000, visualize=False,
               verbose=1)  # 1step:36sec, 1000step:10hours

# After training is done, we save the final weights.
date = datetime.datetime.now()

print('Save model...')
if args.lstm:
    dqn.save_weights('weights/dqn_lstm_{0}_weights_{1}_{2}_{3}_{4}_{5}.h5f'.format(
        ENV_NAME, date.year, date.month, date.day, date.hour, date.minute), overwrite=False)
if args.mlp:
    dqn.save_weights('weights/dqn_mlp_{0}_weights_{1}_{2}_{3}_{4}_{5}.h5f'.format(
        ENV_NAME, date.year, date.month, date.day, date.hour, date.minute), overwrite=False)

# Finally, evaluate our algorithm for 5 episodes.
# dqn.test(env, nb_episodes=5, visualize=True)

# plot results
# loss = hist.history['loss']
# val_loss = hist.history['val_loss']

# epochs = len(loss)
# plt.plot(range(epochs), loss, marker='.', label='acc')
# plt.plot(range(epochs), val_loss, marker='.', label='val_acc')
# plt.legend(loc='best')
# plt.grid()
# plt.xlabel('epoch')
# plt.ylabel('acc')
# plt.show()
