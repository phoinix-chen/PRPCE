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


from typing import List

from utils.wrapper import (
    AD_CS_PIN,
    AD_RST_PIN,
    adc_pin_init,
    chip_select,
    delay,
    gpo_high,
    gpo_low,
    spi_read,
    spi_write,
    termination,
    wait_data_ready,
)

""" Gain Channel """
# GAIN = {2**n: n for n in range(7)}
GAIN = {
    1: 0,  # default
    2: 1,
    4: 2,
    8: 3,
    16: 4,
    32: 5,
    64: 6,
}


""" Sampling Rate (sample per second) """
SPS = {
    2.5: 0x03,
    5: 0x13,
    10: 0x20,
    15: 0x33,
    25: 0x43,
    30: 0x53,
    50: 0x63,
    60: 0x72,
    100: 0x82,
    500: 0x92,
    1000: 0xA1,
    2000: 0xB0,
    3750: 0xC0,
    7500: 0xD0,
    15000: 0xE0,
    30000: 0xF0,  # default
}


""" Registration definition """
REG_STATUS = 0x00
REG_MUX = 0x01
REG_ADCON = 0x02
REG_DRATE = 0x03
REG_IO = 0x04
REG_OFC0 = 0x05
REG_OFC1 = 0x06
REG_OFC2 = 0x07
REG_FSC0 = 0x08
REG_FSC1 = 0x09
REG_FSC2 = 0x0A

""" Command definition  """
CMD_WAKEUP = 0x00
CMD_RDATA = 0x01
CMD_RDATAC = 0x03
CMD_SDATAC = 0x0F
CMD_RREG = 0x10
CMD_WREG = 0x50
CMD_SELFCAL = 0xF0
CMD_SELFOCAL = 0xF1
CMD_SELFGCAL = 0xF2
CMD_SYSOCAL = 0xF3
CMD_SYSGCAL = 0xF4
CMD_SYNC = 0xFC
CMD_STANDBY = 0xFD
CMD_RESET = 0xFE


class ADS1256:
    def __init__(self, background_noise: int = 19925, diff_mode: bool = False) -> None:
        self.noise = background_noise
        self.diff_mode = diff_mode
        self.__init()

    # Hardware Reset
    def __reset(self) -> None:
        gpo_high(AD_RST_PIN)
        delay(200)
        gpo_low(AD_RST_PIN)
        delay(200)
        gpo_high(AD_RST_PIN)

    @chip_select(AD_CS_PIN)
    def __read_reg_data(self, reg: bytes) -> List[bytes]:
        spi_write([CMD_RREG | reg, 0x00])
        return spi_read(1)

    @chip_select(AD_CS_PIN)
    def __write_reg_data(self, reg: bytes, data: bytes) -> None:
        spi_write([CMD_WREG | reg, 0x00, data])

    @chip_select(AD_CS_PIN)
    def __write_cfg_reg_data(self, data: List[bytes]) -> None:
        spi_write([CMD_WREG | 0, 0x03])
        spi_write(data)

    @chip_select(AD_CS_PIN)
    def __send_command(self, command: bytes) -> None:
        spi_write([command])

    @chip_select(AD_CS_PIN)
    def __read_data(self) -> List[bytes]:
        spi_write([CMD_RDATA])
        return spi_read(3)

    def __process_data(self) -> int:
        wait_data_ready()

        data = self.__read_data()
        result = (data[0] << 16) & 0xFF0000
        result |= (data[1] << 8) & 0xFF00
        result |= (data[2] << 0) & 0xFF

        if result & 0x800000:
            result &= 0xF000000

        return result

    def __config_adc(self, ch_gain: int, data_rate: int) -> None:
        wait_data_ready()

        buffer: List[bytes] = [0] * 8
        buffer[0] = 0 << 3 | 1 << 2 | 0 << 1
        buffer[1] = 0x08
        buffer[2] = 0 << 5 | 0 << 3 | ch_gain << 0
        buffer[3] = data_rate

        self.__write_cfg_reg_data(buffer)
        delay(10)

    def __chip_id(self) -> int:
        wait_data_ready()
        data = self.__read_reg_data(REG_STATUS)
        return data[0] >> 4

    def __init(self) -> None:
        adc_pin_init()
        self.__reset()
        if self.__chip_id() != 3:
            raise AttributeError("Chip ID Read Failed!")
        self.__config_adc(GAIN[1], SPS[30000])
        print("ADS1256 Init Success!")

    def __set_channel(self, channel: int) -> None:
        if not self.diff_mode:
            # Single-ended
            data = (channel << 4) | (1 << 3)
        else:
            # Differential
            match channel:
                case 0:
                    data = (0 << 4) | 1  # AIN0 - AIN1
                case 1:
                    data = (2 << 4) | 3  # AIN2 - AIN3
                case 2:
                    data = (4 << 4) | 5  # AIN4 - AIN5
                case 3:
                    data = (6 << 4) | 7  # AIN6 - AIN7

        self.__write_reg_data(REG_MUX, data)

    def get_channel_value(self, channel: int) -> int:
        if (channel < 0) or not isinstance(channel, int):
            termination(ValueError("Channel index should be a positive integer!"))

        if self.diff_mode and channel > 3:
            termination(ValueError("Channel index should range from 0 to 3!"))
        elif channel > 7:
            termination(ValueError("Channel index should range from 0 to 7!"))

        self.__set_channel(channel)
        self.__send_command(CMD_SYNC)
        delay(10)
        self.__send_command(CMD_WAKEUP)
        value = self.__process_data()
        return value - self.noise

    def get_all_channel_value(self) -> List[int]:
        return [self.get_channel_value(i) for i in range(8)]
