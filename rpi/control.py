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


from csv import writer as write
from time import sleep, time

import numpy as np

from controller.pid import PID
from model.fopdt import FOPDT
from utils.adc import ADS1256
from utils.convert import Converter
from utils.dac import DAC8532
from utils.wrapper import cleanup, termination

PID_GAIN = (-10.941, -1.351, 0)
SET_POINT = 4.2

# Model Kp, tau, theta
MODEL_PARAMS = (-0.347, 14.720, 3.865)

STOP_TIME = 120
TIME_PER_STEP = 1

try:
    # AD/DA Init
    ADC = ADS1256()
    DAC = DAC8532()
    DAC.output_volt(0.0)
    DAC.output_volt(0.0, DAC.CH_B)
    sleep(5)

    # Converter Init
    dig2p = Converter(output_type="Pressure")
    valve2volt = Converter(input_type="Valve", output_type="Voltage")

    # Find Init CV (Pressure)
    digital_val = ADC.get_channel_value(0)
    initial_value = dig2p(digital_val)

    # PID Init
    controller = PID(6, 9)
    # PID Tunning Gain
    controller.gain_adjustment = PID_GAIN

    # FOPDT Model Init
    t = np.arange(start=0, stop=int(STOP_TIME / TIME_PER_STEP))
    mv = np.zeros(len(t))
    cv = np.array([initial_value] + [0] * (len(t) - 1))
    model = FOPDT(mv)
    model.model_params = (*MODEL_PARAMS, initial_value)

    file = "./control_result/pid_control.csv"
    with open(file, mode="w", encoding="utf-8", newline="") as csvfile:
        writer = write(csvfile)
        writer.writerow(["Time consuming", "Valve opening", "Pressure", "Model Predict"])

    start_time = time()
    for i in t:
        digital_val = ADC.get_channel_value(0)
        pressure = dig2p(digital_val)
        valve_opening = round(controller(SET_POINT, pressure), 1)
        DAC.output_volt(valve2volt(valve_opening))

        # Predict Model
        if i < len(t) - 1:
            mv[i] = int(valve_opening) - 6
            model.mv = mv
            cv[i + 1] = model(cv[i], [t[i], t[i + 1]])

        with open(file, mode="a", encoding="utf-8", newline="") as csvfile:
            writer = write(csvfile)
            now = time() - start_time
            writer.writerow(
                [
                    f"{now:.2f}",
                    f"{valve_opening}",
                    f"{pressure:.1f}",
                    f"{cv[i]:.1f}",
                ]
            )
        sleep(TIME_PER_STEP)


except KeyboardInterrupt:
    pass
except Exception as err:
    termination(err)
finally:
    DAC.output_volt(0.0)
    DAC.output_volt(0.0, DAC.CH_B)
    cleanup()
