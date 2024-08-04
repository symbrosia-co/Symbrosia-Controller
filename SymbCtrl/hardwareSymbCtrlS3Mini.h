/*------------------------------------------------------------------------------
  Hardware - Symbrosia Controller
  - define the hardware allocations
  - for a WeMos S3 Mini used in the Mark 2

  16Dec2023 v1.0 A. Cooper
  - initial version

--------------------------------------------------------------------------------

    SymbCtrl - The Symbrosia Aquaculture Controller
    Copyright © 2021 Symbrosia Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
  
------------------------------------------------------------------------------*/
#ifndef hardware
#define hardware

// pin enumeration for the ESP32-S3
#define hdwrGPIO0      0  // GPIO0                         bootstrap, weak pull up
#define hdwrGPIO1      1  // GPIO1,  ADC1_CH0
#define hdwrGPIO2      2  // GPIO2,  ADC1_CH1
#define hdwrGPIO3      3  // GPIO3,  ADC1_CH2              bootstrap
#define hdwrGPIO4      4  // GPIO4,  ADC1_CH3
#define hdwrGPIO5      5  // GPIO5,  ADC1_CH4
#define hdwrGPIO6      6  // GPIO6,  ADC1_CH5
#define hdwrGPIO7      7  // GPIO7,  ADC1_CH6
#define hdwrGPIO8      8  // GPIO8,  ADC1_CH7
#define hdwrGPIO9      9  // GPIO9,  ADC1_CH8
#define hdwrGPIO10    10  // GPIO10, ADC1_CH9
#define hdwrGPIO11    11  // GPIO11, ADC2_CH0
#define hdwrGPIO12    12  // GPIO12, ADC2_CH1
#define hdwrGPIO13    13  // GPIO13, ADC2_CH2
#define hdwrGPIO14    14  // GPIO14, ADC2_CH3
#define hdwrGPIO15    15  // GPIO15, ADC2_CH4, XTAL_32K_P  
#define hdwrGPIO16    16  // GPIO16, ADC2_CH5, XTAL_32K_N
#define hdwrGPIO17    17  // GPIO17, ADC2_CH6
#define hdwrGPIO18    18  // GPIO18, ADC2_CH7
#define hdwrGPIO19    19  // GPIO19, ADC2_CH8, USB D-
#define hdwrGPIO20    20  // GPIO20, ADC2_CH9, USB D+
#define hdwrGPIO21    21  // GPIO21
#define hdwrGPIO26    26  // GPIO26, SPICS1                not available if SPI RAM is used
#define hdwrGPIO27    27  // GPIO27, SPIHD                 not available 
#define hdwrGPIO28    28  // GPIO28, SPIWP                 not available 
#define hdwrGPIO29    29  // GPIO29, SPICS0                not available 
#define hdwrGPIO30    30  // GPIO30, SPICLK                not available 
#define hdwrGPIO31    31  // GPIO31, SPIQ                  not available 
#define hdwrGPIO32    32  // GPIO32, SPID                  not available 
#define hdwrGPIO33    33  // GPIO33, SPIQ4                 not available if octal flash or SPI RAM is used
#define hdwrGPIO34    34  // GPIO34, SPIQ5                 not available if octal flash or SPI RAM is used
#define hdwrGPIO35    35  // GPIO35, SPIQ6                 not available if octal flash or SPI RAM is used
#define hdwrGPIO36    36  // GPIO36, SPIQ7                 not available if octal flash or SPI RAM is used
#define hdwrGPIO37    37  // GPIO37, SPIQ8                 not available if octal flash or SPI RAM is used
#define hdwrGPIO38    38  // GPIO38, SPIDQS                not available if octal flash or SPI RAM is used
#define hdwrGPIO39    39  // GPIO39, MTCK                  JTAG
#define hdwrGPIO40    40  // GPIO40, MTDO                  JTAG
#define hdwrGPIO41    41  // GPIO41, MTDI                  JTAG
#define hdwrGPIO42    42  // GPIO42, MTMS                  JTAG
#define hdwrGPIO43    43  // GPIO43, UART0 TX              console
#define hdwrGPIO44    44  // GPIO44, UART0 RX              console
#define hdwrGPIO45    45  // GPIO45                        bootstrap, weak pull down
#define hdwrGPIO46    46  // GPIO46                        bootstrap, weak pull down
#define hdwrGPIO47    47  // GPIO47, SPICLK_P
#define hdwrGPIO48    48  // GPIO48, SPICLK_N

// analog inputs
#define hdwrAnalogIn0  1  // ADC1 inputs
#define hdwrAnalogIn1  2
#define hdwrAnalogIn2  3
#define hdwrAnalogIn3  4
#define hdwrAnalogIn4  5
#define hdwrAnalogIn5  6
#define hdwrAnalogIn6  7
#define hdwrAnalogIn7  8
// ADC2 conflicts with WiFi use, neglected here

// pin enumeration for Symbrosia controller
#define hdwrEncoderPB 15  // pushbutton input, low on press
#define hdwrEncA      17  // encoder inputs
#define hdwrEncB      21
#define hdwrRelay1    14  // outputs
#define hdwrRelay2     9
#define hdwrOutput1   33
#define hdwrOutput2   37
#define hdwrSPICLK    16  // SPI Port
#define hdwrSPIMOSI   34
#define hdwrSPIMISO   18
#define hdwrSPIAtoDCS 38
#define hdwrI2CSDA    35  // I2C Port
#define hdwrI2CSCL    36
#define hdwrLCDRS      2  // LCD control
#define hdwrLCDE       4
#define hdwrLCDRW      3
#define hdwrLCDD0      5
#define hdwrLCDD1     12
#define hdwrLCDD2      6
#define hdwrLCDD3     13
#define hdwrLCDD4      7
#define hdwrLCDD5     11
#define hdwrLCDD6      8
#define hdwrLCDD7     10
#define hdwrRGBLED    47  // RBG LED

#endif
//- End hardware.h -------------------------------------------------------------
