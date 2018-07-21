import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='ccxt_bitmex-v0',
    entry_point='gym_ccxt_bitmex.envs:CcxtBitmexEnv',
    timestep_limit=1000,
    reward_threshold=1500.0,
    nondeterministic = True,
)
