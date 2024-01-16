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


from utils.wrapper import DA_CS_PIN, chip_select, dac_pin_init, spi_write, termination


class DAC8532:
    CH_A = 0x30
    CH_B = 0x34
    __DIGITAL_MAX = 65535
    __VOLT_REF = 5.0

    def __init__(self, volt_bias: float = 0.165) -> None:
        self.volt_bias = volt_bias
        dac_pin_init()
        print("DAC8532 Init Success!")

    @chip_select(DA_CS_PIN)
    def __write_data(self, channel: int, int_data: int) -> None:
        spi_write([channel, int_data >> 8, int_data & 0xFF])

    def __is_invalid_param(self, voltage: float, channel: int) -> bool | str:
        if not (0 <= voltage <= self.__VOLT_REF):
            return "Invalid Voltage Output"
        if channel not in [self.CH_A, self.CH_B]:
            return "Invalid Channel Iutput"
        return False

    def output_volt(self, voltage: float, channel: int = CH_A) -> None:
        """
        ### Output the specified voltage to the specified channel.
        ---
        Note:
        - The output voltage must be between `0` and `5` volts !
        - The channel value must be an integer between `CH_A` and `CH_B` !
        """

        if err := self.__is_invalid_param(voltage, channel):
            termination(ValueError(err))

        ref_volt = self.__VOLT_REF + self.volt_bias
        digital_val = (voltage / ref_volt) * self.__DIGITAL_MAX
        self.__write_data(channel, int(digital_val))
