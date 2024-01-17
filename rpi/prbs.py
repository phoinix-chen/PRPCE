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
from random import randint
from time import sleep, time

from utils.adc import ADS1256
from utils.convert import Converter
from utils.dac import DAC8532
from utils.wrapper import cleanup, termination

try:
    ADC = ADS1256()
    DAC = DAC8532()
    dig2p = Converter(output_type="Pressure")
    valve2volt = Converter(input_type="Valve", output_type="Voltage")

    DAC.output_volt(0.0)
    DAC.output_volt(0.0, DAC.CH_B)
    sleep(5)

    file = "./multi_step_data/multi_step_change.csv"
    with open(file, mode="w", encoding="utf-8", newline="") as csvfile:
        writer = write(csvfile)
        writer.writerow(["Time consuming", "Valve opening", "Pressure"])

    times = 7
    sample_lst = [6, 9, 7, 8, 9, 6, 8]
    print(sample_lst)
    time_per_step = 0

    start_time = time()
    for step in range(times):
        valve_opening = sample_lst[step]

        time_per_step += 60 + randint(-10, 20)
        while (now := time() - start_time) <= time_per_step:
            DAC.output_volt(valve2volt(valve_opening))
            sleep(1)
            digital_val = ADC.get_channel_value(0)
            pressure = dig2p(digital_val)

            with open(file, mode="a", encoding="utf-8", newline="") as csvfile:
                writer = write(csvfile)
                writer.writerow(
                    [
                        f"{now:.2f}",
                        f"{valve_opening}",
                        f"{pressure:.1f}",
                    ]
                )


except KeyboardInterrupt:
    pass
except Exception as err:
    termination(err)
finally:
    DAC.output_volt(0.0)
    DAC.output_volt(0.0, DAC.CH_B)
    cleanup()
