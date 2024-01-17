# Copyright (C) 2024 Phoínix Chen
#
# This file is part of PRPCE.
#
# PRPCE is free software: you can redistribute it and/or modify it under the terms of
# the GNU Lesser General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# PRPCE is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with
# PRPCE. If not, see <https://www.gnu.org/licenses/>.


import matplotlib.pyplot as plt
import numpy as np
from pandas import read_csv
from scipy.integrate import odeint
from scipy.interpolate import interp1d
from scipy.optimize import minimize

# Import CSV data file
data = read_csv("./data/multi_step_change.csv")
t = data["Time consuming"].values - data["Time consuming"].values[0]
u = data["Valve opening"].values
yp = data["Pressure"].values
u0 = u[0]
yp0 = yp[0]

# specify number of steps
ns = len(t)
delta_t = t[1] - t[0]
# create linear interpolation of the u data versus time
uf = interp1d(t, u)


# define first-order plus dead-time approximation
def fopdt(y, t, uf, k, tau, theta):
    # arguments
    #  y      = output
    #  t      = time
    #  uf     = input linear function (for time shift)
    #  k, tau, theta = model gain, time constant, delay

    try:
        if (t - theta) <= 0:  # noqa: SIM108
            um = uf(0.0)
        else:
            # time shift
            um = uf(t - theta)
    except Exception:
        um = u0

    # calculate derivative
    dydt = (-(y - yp0) + k * (um - u0)) / tau
    return dydt


# simulate FOPDT model with x=[k,tau,theta]
def sim_model(x):
    # input arguments
    k, tau, theta = x
    # storage for model values
    y = np.zeros(ns)  # model
    # initial condition
    y[0] = yp0
    # loop through time steps
    for i in range(0, ns - 1):
        ts = [t[i], t[i + 1]]
        y1 = odeint(fopdt, y[i], ts, args=(uf, k, tau, theta))
        y[i + 1] = y1[-1][0]
    return y


# define objective function (RSS)
def objective(x):
    y_model = sim_model(x)
    obj = 0.0
    for i in range(len(y_model)):
        obj += (y_model[i] - yp[i]) ** 2

    return obj


if __name__ == "__main__":
    # initial guess
    x0 = np.array([-1.0, 10.0, 1.0])

    # show initial objective
    print(f"Initial RSS:\t{objective(x0):.5f}")

    # optimize k, tau, theta
    sol = minimize(objective, x0).x

    # show final objective
    print(f"Final RSS:\t{objective(sol):.5f}")
    print(f"Kp:\t{sol[0]:.3f}")
    print(f"tau:\t{sol[1]:.3f}")
    print(f"theta:\t{sol[2]:.3f}")

    # plot results
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(t, yp, "b-", linewidth=3, label="Process Data")
    plt.plot(t, sim_model(sol), "r--", linewidth=2, label="Optimized FOPDT")
    plt.ylabel("Preassure (bar)")
    plt.subplot(2, 1, 2)
    plt.plot(t, u, "b-", linewidth=3, label="Measured")
    plt.plot(t, uf(t), "r--", linewidth=2, label="Interpolated")
    plt.ylabel("Valve Opening (%)")
    plt.xlabel("Time (s)")
    plt.show()
