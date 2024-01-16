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
from scipy.optimize import minimize

from fopdt import FOPDT
from pid import PID

t = np.arange(start=0, stop=200)


def refresh(x):
    initial_value = 5.2
    starting_time = 10

    # Model param
    _gain, _tau, _dead_time = -0.347, 14.716, 3.866
    _kp, _ki = x
    _kd = 0

    # Data array init
    sp = np.zeros(len(t))
    cv = np.zeros(len(t))
    mv = np.zeros(len(t))
    p_val = np.zeros(len(t))
    i_val = np.zeros(len(t))
    d_val = np.zeros(len(t))

    # PID
    pid = PID()
    pid.gain_adjustment = (_kp, _ki, _kd)

    # FOPDT model
    model = FOPDT(mv)
    model.model_params = (_gain, _tau, _dead_time, initial_value)

    # Initial value of CV
    cv[0] = initial_value

    for i in t:
        if i < len(t) - 1:
            if i < starting_time:
                sp[i] = initial_value
            else:
                sp[i] = 4.3

            # calculate MV
            mv[i] = pid(sp[i], cv[i])
            model.mv = mv

            # calculate CV
            cv[i + 1] = model(cv[i], [t[i], t[i + 1]])

            p_val[i], i_val[i], d_val[i] = pid.element_value
        else:
            # Remove endpoint
            sp[i] = sp[i - 1]
            mv[i] = mv[i - 1]
            p_val[i] = p_val[i - 1]
            i_val[i] = i_val[i - 1]
            d_val[i] = d_val[i - 1]
    return sp, cv, mv


# define objective function (RSS)
def objective(x):
    sp, cv, _ = refresh(x)
    obj = 0.0
    for i in range(len(cv)):
        obj += (cv[i] - sp[i]) ** 2
    return obj


if __name__ == "__main__":
    # initial of K_P, K_I
    x0 = np.array([-12.259, -1.481])

    # show initial objective
    print(f"Initial RSS:\t{objective(x0):.5f}")

    # optimize K_P, K_I
    sol = minimize(objective, x0).x

    # show final objective
    print(f"Final RSS:\t{objective(sol):.5f}")
    print(f"Kp:\t{sol[0]:.3f}")
    print(f"Ki:\t{sol[1]:.3f}")

    sp_o, cv_o, mv_o = refresh(x0)
    sp, cv, mv = refresh(sol)

    # plot results
    plt.figure()
    plt.plot(t, sp, color="purple", linewidth=1.5, label="SP")
    plt.plot(t, cv_o, color="blue", linewidth=1.5, label="CV pre opt")
    plt.plot(t, cv, color="red", linewidth=1.5, label="CV")
    ### If you want to observe the MV changes at the same time,
    ### uncomment the following sentence:
    # plt.plot(t, mv, color="green", linewidth=1.5, label="MV")
    plt.title(f"Kp:{sol[0]:.3f}     Ki:{sol[1]:.3f}")
    plt.legend(loc="upper right")
    plt.show()
