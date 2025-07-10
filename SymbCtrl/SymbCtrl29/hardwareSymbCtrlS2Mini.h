/*------------------------------------------------------------------------------
  Hardware - Symbrosia Controller
  - define the hardware allocations
  - for a WeMos S2 Mini used in the Mark 2

  16Dec2023 v1.0 A. Cooper
  - initial version
  20Mar2024 v2.4 A. Cooper
  - Tested and working
  - Conflict on GPIO15, S2 Mini is onboard LED control, SymbCtrl uses this for
   the encoder pushbutton, both are pulled up: 2k onboard, 10k on SymbCtrl,
   thus everything works even if the LED turns off when you push the button;)
  23Apr2024 v2.5 A. Cooper
  - fixed incorrect pin on Digital Output 1 33 to 40

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

// pin enumeration for the ESP32-S2
#define hdwrGPIO0      0  // GPIO0                                           bootstrap, weak pull up
#define hdwrGPIO1      1  // GPIO1,  TOUCH1,   ADC1_CH0
#define hdwrGPIO2      2  // GPIO2,  TOUCH2,   ADC1_CH1
#define hdwrGPIO3      3  // GPIO3,  TOUCH3,   ADC1_CH2
#define hdwrGPIO4      4  // GPIO4,  TOUCH4,   ADC1_CH3
#define hdwrGPIO5      5  // GPIO5,  TOUCH5,   ADC1_CH4
#define hdwrGPIO6      6  // GPIO6,  TOUCH6,   ADC1_CH5
#define hdwrGPIO7      7  // GPIO7,  TOUCH7,   ADC1_CH6
#define hdwrGPIO8      8  // GPIO8,  TOUCH8,   ADC1_CH7
#define hdwrGPIO9      9  // GPIO9,  TOUCH9,   ADC1_CH8, FSPIHD
#define hdwrGPIO10    10  // GPIO10, TOUCH10,  ADC1_CH9, FSPICS0,   FSPIIO4
#define hdwrGPIO11    11  // GPIO11, TOUCH11,  ADC2_CH0, FSPID,     FSPIIO5
#define hdwrGPIO12    12  // GPIO12, TOUCH12,  ADC2_CH1, FSPICLK,   FSPIIO6
#define hdwrGPIO13    13  // GPIO13, TOUCH13,  ADC2_CH2, FSPIQ,     FSPIIO7
#define hdwrGPIO14    14  // GPIO14, TOUCH14,  ADC2_CH3, FSPIWP,    FSPIDQS
#define hdwrGPIO15    15  // GPIO15, U0RTS,    ADC2_CH4, XTAL_32K_P  
#define hdwrGPIO16    16  // GPIO16, U0CTS,    ADC2_CH5, XTAL_32K_N
#define hdwrGPIO17    17  // GPIO17, U1TXD,    ADC2_CH6, DAC_1
#define hdwrGPIO18    18  // GPIO18, U1RXD,    ADC2_CH7, DAC_2,     CLK_OUT3 
#define hdwrGPIO19    19  // GPIO19, U1RTS,    ADC2_CH8, CLK_OUT2,  USB_D-
#define hdwrGPIO20    20  // GPIO20, U1CTS,    ADC2_CH9, CLK_OUT1,  USB_D+
#define hdwrGPIO21    21  // GPIO21
#define hdwrGPIO26    26  // GPIO26, SPICS1                                  SPI0/1
#define hdwrGPIO27    26  // GPIO27, SPIHD                                   SPI0/1
#define hdwrGPIO28    26  // GPIO28, SPIWP                                   SPI0/1
#define hdwrGPIO29    26  // GPIO29, SPICS0                                  SPI0/1
#define hdwrGPIO30    26  // GPIO30, SPICLK                                  SPI0/1
#define hdwrGPIO31    26  // GPIO31, SPIQ                                    SPI0/1
#define hdwrGPIO32    26  // GPIO32, SPID                                    SPI0/1
#define hdwrGPIO33    33  // GPIO33, SPIIO4,   FSPIHD                
#define hdwrGPIO34    34  // GPIO34, SPIIO5,   FSPICS0                 
#define hdwrGPIO35    35  // GPIO35, SPIIO6,   FSPID                 
#define hdwrGPIO36    36  // GPIO36, SPIIO7,   FSPICLK                 
#define hdwrGPIO37    37  // GPIO37, SPIDQS,   FSPIQ                 
#define hdwrGPIO38    38  // GPIO38, FSPIWP                
#define hdwrGPIO39    39  // GPIO39, MTCK,     CLK_OUT3                      JTAG
#define hdwrGPIO40    40  // GPIO40, MTDO,     CLK_OUT2                      JTAG
#define hdwrGPIO41    41  // GPIO41, MTDI,     CLK_OUT1                      JTAG
#define hdwrGPIO42    42  // GPIO42, MTMS                                    JTAG
#define hdwrGPIO43    43  // GPIO43, UART0 TX, CLK_OUT1                      console
#define hdwrGPIO44    44  // GPIO44, UART0 RX, CLK_OUT2                      console
#define hdwrGPIO45    45  // GPIO45                                          bootstrap, weak pull up
#define hdwrGPIO46    46  // GPIO46                                          input only, bootstrap, weak pull up

// analog inputs
#define hdwrAnalogIn0  1  // ADC1 inputs
#define hdwrAnalogIn1  2
#define hdwrAnalogIn2  3
#define hdwrAnalogIn3  4
#define hdwrAnalogIn4  5
#define hdwrAnalogIn5  6
#define hdwrAnalogIn6  7
#define hdwrAnalogIn7  8
#define hdwrAnalogIn8  9
#define hdwrAnalogIn9 10
// ADC2 conflicts with WiFi use, neglected here

// pin enumeration for Symbrosia controller
#define hdwrEncoderPB 15  // pushbutton input, low on press
#define hdwrEncA      17  // encoder inputs
#define hdwrEncB      21
#define hdwrRelay1    14  // outputs
#define hdwrRelay2    13
#define hdwrOutput1   40
#define hdwrOutput2   38
#define hdwrSPICLK    16  // SPI Port
#define hdwrSPIMOSI   34
#define hdwrSPIMISO   18
#define hdwrSPIAtoDCS 36
#define hdwrI2CSDA    33  // I2C Port
#define hdwrI2CSCL    35
#define hdwrLCDRS      3  // LCD control
#define hdwrLCDE       5
#define hdwrLCDRW      2
#define hdwrLCDD0      4
#define hdwrLCDD1      7
#define hdwrLCDD2      6
#define hdwrLCDD3      9
#define hdwrLCDD4      8
#define hdwrLCDD5     11
#define hdwrLCDD6     10
#define hdwrLCDD7     12

#endif
//- End hardware.h -------------------------------------------------------------
