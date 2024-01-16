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


REF = {
    "voltage": 5,
    "digital signal": 0x7FFFFF,
    "ph": 14,
    "valve": 100,
    "flow": 2.5,
    "pressure": 10,
}


class Converter:
    def __init__(
        self, input_type: str = "digital signal", output_type: str = "voltage"
    ) -> None:
        self.__in_type = input_type.lower()
        self.__out_type = output_type.lower()

    def __call__(self, input_value: int | float) -> float:
        return input_value / REF[self.__in_type] * REF[self.__out_type]

    @property
    def input_type(self) -> str:
        return self.__in_type

    @input_type.setter
    def input_type(self, input_type: str) -> None:
        self.__in_type = input_type.lower()

    @property
    def output_type(self) -> str:
        return self.__out_type

    @output_type.setter
    def output_type(self, output_type: str) -> None:
        self.__out_type = output_type.lower()
