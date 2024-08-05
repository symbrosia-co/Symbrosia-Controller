/*------------------------------------------------------------------------------
  Analog to Digital Control - Symbrosia Controller
  - handle the AtoD converter
  - perform a pre-scaling to engineering units using default offset and gain
  - perform filtering on all channels
  - perform calibration using user supplied calibration offset and gain
  - perform thermistor conversion if noted by channel type
  - Written for the ESP32

--- license --------------------------------------------------------------------

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

--- revision record ------------------------------------------------------------

  06Jan2022 A. Cooper
  - initial version
  8Apr2022 A. Cooper
  - rescaled all analog inputs based on prototype
  12Apr2022 A. Cooper
  - added detection/handling for out of range values
  - added thermistor conversion from Genesis
  7Jul2022 A. Cooper
  - fixed calibration bug in WQ sensor
  - added dummy read to switch channels and stabilize readings
  - enlarged averaging table to 40 samples (see #define avgTableSize)
  31Jul2023 A. Cooper
  - removed dummy read
  - preset channel for A/D to allow stabilization during sampling interval
  - enlarged averaging table to 100 samples (see #define avgTableSize)
  17Dec2023 v2.0 A. Cooper
  - revised to use offboard AtoD converters
  - pH is handled by a galvanically isolated MCP3021 single input 10-bit
  - AtoD converter using an I2C interface
  - 8 channels with an MCP3208 12-bit SAR AtoD with an SPI interface
  - rescale all conversion constants for new hardware
  18Jan2024 v2.1 A. Cooper
  - increased averaging substantially
  20Mar2024 v2.4 A. Cooper
  - fixed temperature 2 units bug, using temperature 1 units to flag conversion
  - breaking changes to MCP_ADC library incorporated, now using 0.5.0
  - added offsetHdwr to compensate for average hardware temperature offset
  23Apr2024 v2.5 A.Cooper
  - changed temp out-of-range to -30 to 140 (before cal offsets)
  29Jul2024 v2.6 A. Cooper
  - changed from boxcar average to a tracking average
  - removed single channel read function, never implemented or used
  - added CtoF
  - some corrections to pH temperature calibration, tested successfully
  - apply gain and offset to analog inputs last using selected units
  - add auto detect of MCP3021 I2C address
  - remove MCP3X21 library, use direct calls to Wire (the library is pretty 
  trivial and the address detection was easier without it).
  
------------------------------------------------------------------------------*/

//- library includes -----------------------------------------------------------
#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>

//- Local includes -------------------------------------------------------------
#include "globals.h"
#include "analogCtrl.h"

//- constants ------------------------------------------------------------------
#define pHAtoDDef   0x48
#define minValidTemp -35  
#define maxValidTemp 135
#define adAvgFactor  100
#define sampleAvgInt   4  // sampling interval
   // interval= averaging period * 1000 / (channels * averaging table size )

//- engineering units conversion by channel type -------------------------------
//  - These numbers depend on circuit design, both gains and offsets in the amps
//  as well as the charateristics of the ESP32 ADC
#define offsetWQ     -442 // offset and gain for WQ amp to voltage reading (V)
#define gainWQ  -0.001044 // V/adu @ 10-bit, 0 to 14pH -> 2.68V to 0.2V at A/D
#define offsetPH        7 // gain and offset to convert V to pH
#define gainPH   -0.05916 // assume ideal Nernst value of 59.16mV/pH at 25C
#define offsetTemp  -1200 // offset and gain for temp channels to degrees C
#define gainTemp  0.04817
#define offsetHdwr      0 // a fixed temperature offset to compensate for average hardware
#define offsetVolt      0 // offset and gain for analog channels to V
#define gainVolt 0.002639
#define gainAmp   4.01606 // gain to convert V to mA for analog channels in 4-20mA mode
#define digThresh    2048 // threshold for high/low interpretation of input channel
#define offsetIntT     -3 // a cal correction for internal temp
#define offsetSup       0 // offset and gain for supply voltage
#define gainSup  0.004378

//- instantiate libaries -------------------------------------------------------
MCP3208 AtoDMain(hdwrSPIMISO,hdwrSPIMOSI,hdwrSPICLK);

//- local variables ------------------------------------------------------------
int adCurrent= 0;
unsigned long adLastTime= 0;
uint8_t pHADAddr= pHAtoDDef;

//- functions ------------------------------------------------------------------

AnalogCtrl::AnalogCtrl(){
}

void AnalogCtrl::init(){
  // start pH A/D converter
  Wire.begin(hdwrI2CSCL,hdwrI2CSDA);
  pHADAddr= pHAtoDFind();
  // start main A/D converter
  AtoDMain.begin(hdwrSPIAtoDCS);
} // init

float AnalogCtrl::CtoF(float degC){
  return (degC*1.8) + 32;
} // CtoF

uint8_t AnalogCtrl::pHAtoDFind(){
  uint8_t addr;
  for (uint8_t i=0;i<8;i++){
    addr= pHAtoDDef|i;
    Wire.requestFrom(addr,2U);
    if (Wire.available()==2) return addr;
  }
  return pHAtoDDef;
}

int AnalogCtrl::pHAtoDRead(uint8_t pHADAddr){
  Wire.requestFrom(pHADAddr,2U);
  if (Wire.available()==2) return ((Wire.read() << 6) | (Wire.read() >> 2));
  return 0;
}

void AnalogCtrl::readAll(){
  uint16_t rawRead;
  int nextRead;
  float result;
  float temp;
  int comp;
  // sampling interval timer
  if (millis()<adLastTime) adLastTime= 0; // handle millis rollover
  if (millis()-adLastTime<sampleAvgInt) return;
  adLastTime= millis();
  // sweep through the channels and the averaging array
  if (++adCurrent>6) adCurrent=0;
  // get raw reading
  if (adCurrent==0){
    rawRead= pHAtoDRead(pHADAddr);
  }
  else{
    rawRead= AtoDMain.read(adCurrent-1);
    // preset a/d converter to next channel to stabilize during sampling interval
    nextRead= adCurrent+1;
    if (nextRead>6) nextRead= 1;
    AtoDMain.read(nextRead); 
  }
  // Serial.print(adCurrent);
  // Serial.print(": ");  
  // Serial.print(rawRead);
  // Serial.print("   ");
  // if (adCurrent==8) Serial.println("");
  // averaging
  int factor= adAvgFactor;
  if (abs(rawRead-adAverage[adCurrent])>50)  factor= adAvgFactor/10;
  if (abs(rawRead-adAverage[adCurrent])>1000) factor= 4;
  adAverage[adCurrent]= adAverage[adCurrent]+((rawRead-adAverage[adCurrent])/factor);
  result= adAverage[adCurrent];
  // handle each channel appropriately for type
  if (adCurrent==0){  // WQ input amplifier
    // check sensor in range
    memory.setBool(statWQSensorValid,(result>100 && result<4000));
    // convert to engineering units   
    result= (result+offsetWQ)*gainWQ;
    if (memory.getInt(datWQSensorUnits)==unitsmV) result= result*1000;    
    if (memory.getInt(datWQSensorUnits)==unitspH){
      // temperature compensation?
      comp= memory.getInt(datPHTempComp);
      if (comp>=ioTemp1 && comp<=ioAnalog2){
        comp= comp-ioTemp1;
        if (memory.getBool(statTemp1Valid+comp)){
          temp= memory.getFloat(datTemperature1+(comp*2));
          if (memory.getInt(datTemp1Units+comp)==unitsDegF) temp= (temp-32)*0.5555;
          // Serial.println(-0.000198*(temp+273.15),4);
          result= (result/(-0.000198*(temp+273.15)))+offsetPH; // temp compensated conversion
        }
        else {
          result= (result/gainPH)+offsetPH;
          memory.setBool(statWQSensorValid,false);
        }
      }
      else result= (result/gainPH)+offsetPH;  // ideal Nernst conversion at 25C
      if (result<0.5){
        result= 0.5;
        memory.setBool(statWQSensorValid,false);
      }
      if (result>14.5){
        result= 14.5;
        memory.setBool(statWQSensorValid,false);
      }
      //Serial.println(result);
      result= ((result+memory.getFloat(datWQOffset)-7)*memory.getFloat(datWQGain))+7;
      //Serial.println(result);
      memory.setFloat(datWQ,result);
    }
    else{
      memory.setFloat(datWQ,(result+memory.getFloat(datWQOffset))*memory.getFloat(datWQGain));      
    }
  }
  if (adCurrent==1){  // Temp 1 input amplifier
    // convert to engineering units (degrees C)
    result= (result+offsetTemp)*gainTemp;
    // check for allowable range
    memory.setBool(statTemp1Valid,(result>=minValidTemp && result<=maxValidTemp));
    // apply user calibration and offset
    result= (result+memory.getFloat(datTemp1Offset))*memory.getFloat(datTemp1Gain)+offsetHdwr;
    //convert to deg F?
    if (memory.getInt(datTemp1Units)==unitsDegF) result=result*1.8+32;
    // store result
    memory.setFloat(datTemperature1,result);
  }
  if (adCurrent==2){  // Temp 2 input amplifier
    // convert to engineering units (degrees C)
    result= (result+offsetTemp)*gainTemp;
    // check for allowable range
    memory.setBool(statTemp2Valid,(result>=minValidTemp && result<=maxValidTemp));
    // apply user calibration and offset
    result= (result+memory.getFloat(datTemp2Offset))*memory.getFloat(datTemp2Gain)+offsetHdwr;
    //convert to deg F?
    if (memory.getInt(datTemp2Units)==unitsDegF) result=result*1.8+32;
    // store result
    memory.setFloat(datTemperature2,result);
  }
  if (adCurrent==4){  // Analog 1 input channel
    // check for allowable range
    memory.setBool(statAnalog1Valid,!(result<0 || result>4090));
    // set digital result based on threshold
    memory.setBool(statDigitalIn1,rawRead>digThresh);
    // convert to volts
    result= (result+offsetVolt)*gainVolt;
    // convert to engineering units V, mV, or possibly mA
    if (memory.getUInt(datAnalog1Units)==unitsmA) result= result*gainAmp;
    if (memory.getUInt(datAnalog1Units)==unitsmV) result= result*1000;
    // calibrate
    result= (result+memory.getFloat(datAnalog1Offset))*memory.getFloat(datAnalog1Gain);
    // store result with user gain and offset applied
     memory.setFloat(datAnalog1,result);
  }
  if (adCurrent==3){  // Analog 2 input channel
    // check for allowable range
    memory.setBool(statAnalog2Valid,!(result<0 || result>4090));
    // set digital result based on threshold
    memory.setBool(statDigitalIn2,rawRead>digThresh);
    // convert to volts
    result= (result+offsetVolt)*gainVolt;
    // convert to engineering units V, mV, or possibly mA
    if (memory.getUInt(datAnalog2Units)==unitsmA) result= result*gainAmp;
    if (memory.getUInt(datAnalog2Units)==unitsmV) result= result*1000;
    // calibrate
    result= (result+memory.getFloat(datAnalog2Offset))*memory.getFloat(datAnalog2Gain);
    // store result with user gain and offset applied
     memory.setFloat(datAnalog2,result);
  }
  if (adCurrent==6){  // Internal Temperature
    // find the resistance using voltage divider equation
    result= 10000/((3.3/(float(result)*(2.5/4095)))-1);
    // Use the thermistor B form of the conversion 1/T = 1/To + ln(Rt/Ro)/B (degrees Kelvin)
    result= (1/((log(result/10000)/3950)+(1/298.15)))-273.15+offsetIntT;
    // valid?
    if (result>=-20 && result<=120) memory.setBool(statIntTempValid,true);
    else memory.setBool(statIntTempValid,false);
    //convert to deg F?
    if (memory.getInt(datIntTempUnits)==unitsDegF) result=result*1.8+32; 
    // store result
    memory.setFloat(datIntTemp,result);
  }
  if (adCurrent==5){  // Supply Voltage
    memory.setBool(statSupVoltValid,true);
    // convert to engineering units and store
    memory.setFloat(datSupplyVoltage,(result+offsetSup)*gainSup);
  }
} // readAll

//- End analogCtrl -------------------------------------------------------------
