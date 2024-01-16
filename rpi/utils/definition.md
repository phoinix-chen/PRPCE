## GPIO
### PIN
Pin Define | Pin | Description
-- | -- | --
AD_DRDY_PIN | 17 | ADC Data Ready Pin
AD_RST_PIN | 18 | ADC Reset Pin
AD_CS_PIN | 22 | ADC Chip Select Pin
DA_CS_PIN | 23 | DAC Chip Select Pin

## ADS1256
### Register
Register | Address | Reset Value
-- | -- | --
REG_STATUS | 0x00 | x1H
REG_MUX | 0x01 | 01H
REG_ADCON | 0x02 | 20H
REG_DRATE | 0x03 | F0H
REG_IO | 0x04 | E0H
REG_OFC0 | 0x05 | xxH
REG_OFC1 | 0x06 | xxH
REG_OFC2 | 0x07 | xxH
REG_FSC0 | 0x08 | xxH
REG_FSC1 | 0x09 | xxH
REG_FSC2 | 0x0A | xxH

### Action Command
Command |1st Byte (Hex) | 1st Byte |2nd Byte | Description
-- | -- | -- | -- | --
CMD_WAKEUP | 0x00 | 0000 0000 | | Completes SYNC and Exits Standby Mode
CMD_RDATA | 0x01 | 0000 0001 | | Read Data
CMD_RDATAC | 0x03 | 0000 0011 | | Read Data Continuously
CMD_SDATAC | 0x0F | 0000 1111 | | Stop Read Data Continuously
CMD_RREG | 0x10 | 0001 rrrr | 0000 nnnn |  Read from REG rrrr
CMD_WREG | 0x50 | 0101 rrrr | 0000 nnnn | Write to REG rrrr
CMD_SELFCAL | 0xF0 | 1111 0000 | | Offset and Gain Self-Calibration
CMD_SELFOCAL | 0xF1 | 1111 0001 | | Offset Self-Calibration
CMD_SELFGCAL | 0xF2 | 1111 0010 | | Gain Self-Calibration
CMD_SYSOCAL | 0xF3 | 1111 0011 | | System Offset Calibration
CMD_SYSGCAL | 0xF4 | 1111 0100 | | System Gain Calibration
CMD_SYNC | 0xFC | 1111 1100 | | Synchronize the A/D Conversion
CMD_STANDBY | 0xFD | 1111 1101 | | Begin Standby Mode
CMD_RESET | 0xFE | 1111 1110 | | Reset to Power-Up values