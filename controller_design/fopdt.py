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


from scipy.integrate import odeint as ode


class FOPDT:
    def __init__(self, manipulated_params: list) -> None:
        self.mv = manipulated_params
        self.__gain, self.__tau, self.__dead_time, self.__deviation = 0, 0, 0, 0

    @property
    def model_params(self) -> tuple[float, float, float, float]:
        return self.__gain, self.__tau, self.__dead_time, self.__deviation

    @model_params.setter
    def model_params(self, params: tuple[float, float, float, float]) -> None:
        """
        Setting gain, time constant, dead time, and deviation.
        """
        self.__gain, self.__tau, self.__dead_time, self.__deviation = params

    def __dydt(self, cv, t) -> float:
        temp_t = int(t - self.__dead_time)
        if temp_t <= 0:
            unit_step = 0
        elif temp_t >= len(self.mv):
            unit_step = self.mv[-1]
        else:
            unit_step = self.mv[temp_t]
        return (-(cv - self.__deviation) + self.__gain * unit_step) / self.__tau

    def __call__(self, CV, t):
        return ode(self.__dydt, CV, t)[-1]
