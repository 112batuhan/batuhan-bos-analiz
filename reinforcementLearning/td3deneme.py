import gym

from gym_mtsim import (
    Timeframe, SymbolInfo,
    MtSimulator, OrderType, Order, SymbolNotFound, OrderNotFound,
    MtEnv,
    FOREX_DATA_PATH, STOCKS_DATA_PATH, CRYPTO_DATA_PATH, MIXED_DATA_PATH,
)
from numpy import true_divide
import pytz
from datetime import datetime, timedelta
import pandas as pd
from ta import add_all_ta_features
from ta.utils import dropna
from stable_baselines3 import TD3
from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise
import numpy as np

sim = MtSimulator(
    unit='USD',
    balance=10000.,
    leverage=100.,
    stop_out_level=0.2,
    hedge=False,
)

sim.download_data(
        symbols=['EURUSD'],
        time_range=(
            datetime(2021, 5, 5, tzinfo=pytz.UTC),
            datetime(2021, 9, 7, tzinfo=pytz.UTC)
        ),
        timeframe=Timeframe.M1
    )

sim.symbols_data["EURUSD"] = dropna(sim.symbols_data["EURUSD"])
sim.symbols_data["EURUSD"] = add_all_ta_features(sim.symbols_data["EURUSD"], open="Open", high="High", low="Low", close="Close", volume="Volume")
sim.symbols_data["EURUSD"].dropna(inplace=True, how="all", axis="columns")
sim.symbols_data["EURUSD"].drop(inplace=True, columns=["momentum_kama", "trend_psar_down", "trend_psar_up"])
sim.symbols_data["EURUSD"].dropna(inplace=True)

sim.current_time = datetime(2021, 8, 30, 0, 17, 52, tzinfo=pytz.UTC)

env = MtEnv(
    original_simulator=sim,
    trading_symbols=['EURUSD'],
    window_size=1,
    # time_points=[desired time points ...],
    hold_threshold=0.5,
    close_threshold=0.5,
    fee=lambda symbol: {
        'EURUSD': max(0., np.random.normal(0.0002, 0.00003)),
    }[symbol],
    symbol_max_orders=2,
)



n_actions = env.action_space.shape[-1]
action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))

model = TD3("MlpPolicy", env, verbose=1, action_noise=action_noise, train_freq=(1,"step"), learning_starts=10000)
model.learn(total_timesteps=1000000, log_interval=1)

observation = env.reset()
while True:
    action, _states = model.predict(observation)
    observation, reward, done, info = env.step(action)
    
    if done:
        break

env.render('advanced_figure', time_format="%Y-%m-%d")