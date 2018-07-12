# gym-ccxt_bitmex


## ccxt_bitmex

The ccxt_bitmex task initializes a single offensive agent on the field and rewards +1 for scoring a goal and 0 otherwise. In order to score a goal, the agent will need to know how to approach the ball and kick towards the goal. The sparse nature of the goal reward makes this task very difficult to accomplish.

# Installation

```bash
$ pip install keras
$ pip install gym
$ pip install keras-rl
$ pip install ccxt
$ pip install simplejson

run by LSTM
$ python ccxt_bitmex_main.py --lstm
run by MLP
$ python ccxt_bitmex_main.py --mlp

```

# Caution
* ccxt_bitmex_util2.pyに書いてあるapi key ,などは西峯のキーなので変えて使ってください。 
* オプションをつけずに実行すれば、LSTMが採用されます。