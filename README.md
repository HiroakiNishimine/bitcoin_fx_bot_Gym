# gym-ccxt_bitmex
Open AI Gymでbitmexにおいて強化学習で取引を行うソフトです。

# Requirements
* Python 3
* CUDA >= 8.0
* CUDNN >= 6.0
* TensorFlow-GPU >= 1.3
* Nvidia製GPU

# Installation

```bash
$ conda create -n bitmex python=3.6 anaconda
$ source activate bitmex
$ pip install tensorflow-gpu
$ pip install keras
$ pip install gym
$ pip install keras-rl
$ pip install ccxt
$ pip install simplejson

run by LSTM
$ python ccxt_bitmex_main.py --lstm 1
run by MLP
$ python ccxt_bitmex_main.py --mlp 1

```

# Caution
* ccxt_bitmex_util2.pyに書いてあるapi keyを自分のものに変えて使ってください。 
* オプションをつけずに実行すれば、LSTMが採用されます。
* Ubuntu 16.04, CUDA = 8.0, CUDNN = 6.0, TensorFlow-GPU = 1.4, Keras = 2.1.6で動作確認をしています。
