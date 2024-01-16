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


from time import sleep
from typing import Callable, List, NoReturn

import RPi.GPIO as GPIO
import spidev


def delay(millisecond: int):
    sleep(millisecond // 1000)


#####   GPIO Wrapper
GPIO.setwarnings(False)


def gpo_low(pin: int) -> None:
    GPIO.output(pin, GPIO.LOW)


def gpo_high(pin: int) -> None:
    GPIO.output(pin, GPIO.HIGH)


def chip_select(cs_pin: int):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            gpo_low(cs_pin)  # CS/SS Low
            result = func(*args, **kwargs)
            gpo_high(cs_pin)  # CS/SS High
            return result

        return wrapper

    return decorator


def cleanup() -> None:
    GPIO.cleanup()
    print("\nSafely kill processes")


def termination(error: Exception) -> NoReturn:
    cleanup()
    raise error


# PIN
GPIO.setmode(GPIO.BCM)
AD_DRDY_PIN = 17
AD_RST_PIN = 18
AD_CS_PIN = 22
DA_CS_PIN = 23


def adc_pin_init() -> None | NoReturn:
    try:
        GPIO.setup(AD_CS_PIN, GPIO.OUT)
        GPIO.setup(AD_DRDY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(AD_RST_PIN, GPIO.OUT)
    except Exception as error:
        termination(error)


def dac_pin_init() -> None | NoReturn:
    try:
        GPIO.setup(DA_CS_PIN, GPIO.OUT)
    except Exception as error:
        termination(error)


def wait_data_ready() -> None | NoReturn:
    for _ in range(400000):
        if GPIO.input(AD_DRDY_PIN) == 0:
            return
    termination(RuntimeError("Time Out"))


##### SPI Wrapper
spi = spidev.SpiDev()
bus, device = 0, 0
spi.open(bus, device)
spi.max_speed_hz = 20000
spi.mode = 0b01


def spi_write(reg: List[bytes]) -> None:
    spi.writebytes(reg)


def spi_read(n_bytes: int) -> List[bytes]:
    return spi.readbytes(n_bytes)
