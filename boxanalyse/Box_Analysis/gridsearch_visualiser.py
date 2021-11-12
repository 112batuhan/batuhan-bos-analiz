from mpl_toolkits import mplot3d
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys

symbol = sys.argv[0]
choices = ["score", "average_seconds", "steps", "total_boxes"]

columns = ["box_percentage", "box_breakout", "peak_breakout", "score", "average_seconds", "steps", "total_boxes"]
df = pd.read_csv(f"outputs\\box_grid_search\\gridsearch_{symbol}.csv", names=columns)
df = df.loc[df['peak_breakout']<1] #over
df = df.loc[df["box_breakout"]>0.1]
df = df.loc[df["box_percentage"]>0.02]
print(df)
print(df.info)

for z_axis in choices:

    fig = plt.figure(z_axis ,figsize = (14,8))
    fig.suptitle(f"{z_axis} {symbol}".upper(), fontsize=20)
    ax = plt.axes(projection='3d')
    ax.set_xlabel('box_breakout')
    ax.set_ylabel('peak_breakout')
    ax.set_zlabel(z_axis)

    cmap_string = "Spectral"

    norm = mpl.colors.Normalize(vmin=df["box_percentage"].min(), vmax=df["box_percentage"].max())
    mappable = plt.cm.ScalarMappable(cmap=cmap_string, norm=norm)

    cbar = fig.colorbar(mappable, ax = ax, orientation="horizontal", fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel('box_size')

    ax.scatter3D(df["box_breakout"], df["peak_breakout"], df[z_axis], c=df["box_percentage"], cmap=cmap_string)
    #ax.scatter3D(df["box_percentage"], df["box_breakout"], df["peak_breakout"], c=df["score"], cmap='magma')

plt.show()