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


from types import MappingProxyType


class PID:
    def __init__(self) -> None:
        # kp , ki, kd value
        self.__kp, self.__ki, self.__kd = 0, 0, 0

        # PID output limit
        self.__limits = MappingProxyType({"min": 0, "max": 5})

        # P, I, D value
        self.__p_val = 0
        self.__i_val = 0
        self.__d_val = 0

        # Previous error (In order to calculate D value)
        self.__pre_err = 0
        self.__pre_mv = 0

        # Verify that D is initialized before each call to the new PID
        self.__d_init = False

    # Get element value
    @property
    def element_value(self) -> tuple[float, float, float]:
        """
        ## Get Values of Proportional, Integral, and Derivative.

        #### Return value:
        (float, float, float)
        """
        return self.__p_val, self.__i_val, self.__d_val

    # Adjust the value of Kp, Ki, and Kd
    @property
    def gain_adjustment(self) -> tuple[float, float, float]:
        return self.__kp, self.__ki, self.__kd

    @gain_adjustment.setter
    def gain_adjustment(self, value: tuple[float, float, float]) -> None:
        """
        Setting Kp, Ki, and Kd.
        """
        self.__kp, self.__ki, self.__kd = value

    def __confine(self, value: float, limits: tuple) -> float:
        lower, upper = limits
        if value is None:
            return None
        if (upper is None) or (lower is None):
            return value
        (lower, upper) = (lower, upper) if lower < upper else (upper, lower)
        return lower if value < lower else (upper if value > upper else value)

    def __call__(self, SP, CV) -> float:
        # Setpoint(SP): The target value for PV
        # Controlled variable(CV): The current measured value
        # Manipulated variable(MV)

        err = SP - CV
        # Avoid outputting 0 when error is 0
        if err == 0:
            return self.__pre_mv

        # P
        self.__p_val = self.__kp * err

        # I
        temp_i = self.__ki * err
        if self.__limits["min"] < self.__pre_mv < self.__limits["max"]:
            self.__i_val += temp_i
        if self.__kp == 0:
            if (self.__pre_mv == self.__limits["min"]) and (temp_i > 0):  # noqa: SIM114
                self.__i_val += temp_i
            elif (self.__pre_mv == self.__limits["max"]) and (temp_i < 0):
                self.__i_val += temp_i

        # D
        # In order not to oscillate when SP changes, use CV instead.
        errD = -CV
        if self.__d_init is False:
            self.__d_val = 0
            self.__d_init = True
        else:
            self.__d_val = self.__kd * (errD - self.__pre_err)
        self.__pre_err = errD

        # Manipulated variable(MV)
        mv = self.__p_val + self.__i_val + self.__d_val + self.__limits["min"]
        mv = self.__confine(mv, self.__limits.values())
        self.__pre_mv = mv

        # Return
        return mv

    def reset(self) -> None:
        """
        ## Reset the PID controller internals.
        """
        self.__p_val = 0
        self.__i_val = self.__confine(0, self.__limits.values())
        self.__d_val = 0
        self.__pre_err = 0
        self.__pre_mv = 0
