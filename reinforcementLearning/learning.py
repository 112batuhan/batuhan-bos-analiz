from numpy import true_divide
import pytz
from datetime import datetime, timedelta
from gym_mtsim import MtSimulator, OrderType, Timeframe, FOREX_DATA_PATH
import pandas as pd
from ta import add_all_ta_features
from ta.utils import dropna

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


order1 = sim.create_order(
    order_type=OrderType.Buy,
    symbol='EURUSD',
    volume=1.,
    fee=0.0003,
)

sim.tick(timedelta(minutes=2))

order2 = sim.create_order(
    order_type=OrderType.Sell,
    symbol='EURUSD',
    volume=2.,
    fee=0.01,
)

sim.tick(timedelta(minutes=5))

state = sim.get_state()

print(
    f"balance: {state['balance']}, equity: {state['equity']}, margin: {state['margin']}\n"
    f"free_margin: {state['free_margin']}, margin_level: {state['margin_level']}\n"
)
print(state['orders'])


for order in sim.orders:
    sim.close_order(order)

state = sim.get_state()

print(
    f"balance: {state['balance']}, equity: {state['equity']}, margin: {state['margin']}\n"
    f"free_margin: {state['free_margin']}, margin_level: {state['margin_level']}\n"
)
