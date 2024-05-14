import random
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import csv

#plt.style.use('fivethirtyeight')

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')



namafile = 'visualize.csv'
header1 = "x_coord"
header2 = "y_coord"
header3 = "z_coord"
header4 = "type"

index = count()


def animate(i):
    with open(namafile, newline='') as csvfile:
        csv_reader = csv.reader(csvfile)

        x_particles = []
        y_particles = []
        z_particles = []
        x_anchor = []
        y_anchor = []
        z_anchor = []

        for row in csv_reader:
            if len(row)==4 and row[3]== "particle":
                x_particles.append(float(row[0]))
                y_particles.append(float(row[1]))
                z_particles.append(float(row[2]))
            elif len(row)==4 and row[3]== "anchor":
                x_anchor.append(float(row[0]))
                y_anchor.append(float(row[1]))
                z_anchor.append(float(row[2]))


        plt.cla()

        ax.scatter(x_particles, y_particles, z_particles, marker="x", s = 1)
        ax.scatter(x_anchor, y_anchor, z_anchor)
        ax.set_xlim(-3, 3)
        ax.set_ylim(0, 5)
        ax.set_zlim(-1, 3)

        ax.autoscale(enable = False)




ani = FuncAnimation(plt.gcf(), animate, interval=200)

#plt.tight_layout()
plt.show()
