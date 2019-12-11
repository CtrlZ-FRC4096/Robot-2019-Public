#include <Wire.h>
#include <QTRSensors.h>
#include <Adafruit_NeoPixel.h>


#define i2cAddress 0x10

#define TIMEOUT       2500  // waits for 2500 microseconds for sensor outputs to go low
#define EMITTER_PIN   255     // emitter is controlled by digital pin 2

#define LED_PIN1 12
#define LED_PIN2 13
#define NUMPIXELS 60

unsigned int position;


//unsigned int CalibratedMinVals[] = {736, 124, 8, 124, 124, 8, 8, 124, 124, 124, 124, 368, 368, 124, 244, 124, 124, 124, 128, 240, 124, 360, 360};
//unsigned int CalibratedMaxVals[] = {2500, 2500, 240, 360, 604, 240, 240, 1468, 2500, 2500, 728, 2500, 2500, 608, 2500, 364, 484, 244, 364, 484, 244, 2500, 2500};
//unsigned int CalibratedMinVals[] = {2500, 248, 8, 124, 124, 8, 8, 124, 248, 248, 248, 508, 1028, 248, 376, 124, 124, 124, 124, 244, 124, 376, 500};
//unsigned int CalibratedMaxVals[] = {2500, 2500, 236, 360, 600, 236, 236, 852, 2500, 1348, 600, 2500, 2500, 600, 2500, 360, 472, 240, 360, 476, 240, 2500, 2500};
//unsigned int CalibratedMinVals[] = {2500, 244, 8, 124, 124, 8, 12, 128, 240, 240, 240, 484, 864, 240, 364, 124, 124, 124, 124, 240, 124, 360, 484};
//unsigned int CalibratedMaxVals[] = {2500, 2500, 240, 360, 484, 240, 240, 856, 2500, 1612, 608, 2500, 2500, 608, 2500, 360, 360, 240, 360, 484, 240, 2500, 2500};

// Midwest on real field. Seems to work even though array was moved upwards later.
//unsigned int CalibratedMinVals[] = {1744, 244, 8, 124, 124, 8, 124, 124, 240, 240, 236, 484, 736, 240, 364, 128, 124, 124, 124, 240, 124, 360, 484};
//unsigned int CalibratedMaxVals[] = {2500, 2500, 240, 360, 608, 240, 240, 856, 2500, 1620, 608, 2500, 2500, 612, 2500, 364, 484, 240, 364, 484, 240, 2500, 2500};
// Second set of values from real field calibration, decided to use first set instead.
//1996 240 8 124 124 8 8 124 244 240 128 484 732 240 364 124 124 124 124 240 124 360 360
//2500 2500 240 360 608 236 240 852 2500 1352 608 2500 2500 608 2500 360 484 240 360 484 240 2500 2500

// Midwest on practice field, when array at LOW position
//unsigned int CalibratedMinVals[] = {2500, 240, 124, 124, 124, 8, 124, 240, 240, 240, 240, 604, 2500, 240, 360, 240, 236, 124, 240, 240, 124, 480, 480};
//unsigned int CalibratedMaxVals[] = {2500, 2500, 356, 476, 728, 236, 240, 1476, 2500, 2500, 852, 2500, 2500, 724, 2500, 480, 480, 360, 480, 480, 240, 2500, 2500};

// Midwest on practice field, when array at HIGH position
unsigned int CalibratedMinVals[] = {2500, 724, 124, 240, 360, 124, 124, 360, 600, 480, 360, 2500, 2500, 360, 728, 240, 240, 240, 240, 244, 240, 2500, 2500};
unsigned int CalibratedMaxVals[] = {2500, 2500, 356, 476, 972, 236, 236, 2500, 2500, 2500, 848, 2500, 2500, 720, 2500, 472, 472, 356, 472, 476, 236, 2500, 2500};


/*
 *  Ardunio Mega pinout
 *  Digital IO: 22-53
 *  Analog in: A0-A15
 *  Analog/PWM out OR Digital IO: 2-13, 44, 45, 46
*/

#define numSensors 23

QTRSensorsRC lightSensors((unsigned char[]){22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44}, numSensors, TIMEOUT, EMITTER_PIN);
Adafruit_NeoPixel strip1 = Adafruit_NeoPixel(NUMPIXELS, LED_PIN1, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip2 = Adafruit_NeoPixel(NUMPIXELS, LED_PIN2, NEO_GRB + NEO_KHZ800);

unsigned int sensorValues[numSensors];

char ledPattern, newPattern;
int orangeEnd, blueEnd;
boolean LEDinit = false;
boolean flashInit = false;
unsigned long startTime;
unsigned long previousLedTime = 0;
int glowBrightness = 0;

void setup() {
  position = 0;

  Wire.begin(i2cAddress);
  Wire.onRequest(sendData);
  Wire.onReceive(switchLEDs);
  Serial.begin(9600);
  delay(500);
  pinMode(13, OUTPUT);

  manualCalibrate();

//  autoCalibrate(CalibratedMaxVals, CalibratedMinVals);

  Serial.println();
//  delay(1000);
  startTime = millis();
  strip1.begin();
  strip2.begin();
  ledPattern = 'a';
//  ledPattern = 'b';
//  ledPattern = 'c';
}

void loop() {
  // read calibrated sensor values and obtain a measure of the line position from 0 to 15000
  position = lightSensors.readLine(sensorValues, QTR_EMITTERS_ON, true);
  runLEDs(ledPattern);

  // print the sensor values as numbers from 0 to 1000, where 0 means maximum reflectance and
  // 1000 means minimum reflectance, followed by the line position
  //THIS IS FOR DEBUGGING ONLY
//    for (unsigned char i = 0; i < numSensors; i++)
//  {
//    Serial.print(sensorValues[i]);
//    Serial.print('\t');
//  }
//  Serial.println();
//  Serial.println(position); // comment this line out if you are using raw values
//  delay(250);


}

void sendData()
{
//  The Arduino code takes the sensor read values and finds the sensor in the middle.
//  We can then return a 6 bit number (0-63) that will indicate this centered position.
  unsigned char centerSensor = position/1000;

//  127 will be our "not found" value
  if(centerSensor == 0 || centerSensor == numSensors-1) centerSensor = 127;
  Wire.write(centerSensor);
}

void switchLEDs(int i)
{
//  The Arduino code takes the sensor read values and finds the sensor in the middle.
//  We can then return a 6 bit number (0-63) that will indicate this centered position.
  while(Wire.available())
  {
    newPattern = Wire.read();
    Serial.println(newPattern);
    if(newPattern != ledPattern)
    {
      startTime = millis();
    }
    ledPattern = newPattern;
  }
}

void manualCalibrate()
{
  digitalWrite(13, HIGH);    // turn on Arduino's LED to indicate we are in calibration mode
  for (int i = 0; i < 400; i++)  // make the calibration take about 10 seconds
  {
    lightSensors.calibrate();
  }
  digitalWrite(13, LOW);     // turn off Arduino's LED to indicate we are through with calibration

  // print the calibration minimum values measured when emitters were on
    for (int i = 0; i < numSensors; i++)
  {
    Serial.print(lightSensors.calibratedMinimumOn[i]);
    Serial.print(' ');
  }
  Serial.println();

  // print the calibration maximum values measured when emitters were on
    for (int i = 0; i < numSensors; i++)
  {
    Serial.print(lightSensors.calibratedMaximumOn[i]);
    Serial.print(' ');
  }
  Serial.println();
}

void autoCalibrate(unsigned int *maxValsList, unsigned int *minValsList)
{
  lightSensors.calibratePreset(maxValsList, minValsList);

  // print the calibration minimum values measured when emitters were on
    for (int i = 0; i < numSensors; i++)
  {
    Serial.print(lightSensors.calibratedMinimumOn[i]);
    Serial.print(' ');
  }
  Serial.println();

  // print the calibration maximum values measured when emitters were on
    for (int i = 0; i < numSensors; i++)
  {
    Serial.print(lightSensors.calibratedMaximumOn[i]);
    Serial.print(' ');
  }
  Serial.println();
}

void runLEDs(char pattern)
{
    switch(pattern)
    {
      case 'a':
        OrangeBlueChase(25);
        break;
      case 'b':
        FlashGreen(200, 4000);
        break;
      case 'c':
        GlowRed(5);
        break;
    }
}

void OrangeBlueChase(uint8_t wait)
{
  if(!LEDinit)
  {
      for(orangeEnd = 0; orangeEnd < NUMPIXELS/2; orangeEnd++)
  {
    strip1.setPixelColor(orangeEnd, 255, 40, 0);
    strip2.setPixelColor(orangeEnd, 255, 40, 0);
  }
  for(blueEnd = orangeEnd + 1; blueEnd < NUMPIXELS; blueEnd++)
  {
    strip1.setPixelColor(blueEnd, 0, 0, 255);
    strip2.setPixelColor(blueEnd, 0, 0, 255);
  }
  strip1.show();
  strip2.show();
  LEDinit = true;
  }

  if((millis() - previousLedTime) > wait)
  {
    previousLedTime = millis();
    strip1.setPixelColor(blueEnd % NUMPIXELS, 0, 0, 255);
    strip1.setPixelColor(orangeEnd % NUMPIXELS, 255, 40, 0);
    strip2.setPixelColor(blueEnd % NUMPIXELS, 0, 0, 255);
    strip2.setPixelColor(orangeEnd % NUMPIXELS, 255, 40, 0);
    strip1.show();
    strip2.show();
    blueEnd++;
    orangeEnd++;
    blueEnd %= NUMPIXELS;
    orangeEnd %= NUMPIXELS;
  }
}

void FlashGreen(uint8_t wait, int duration)
{
  if((millis() - previousLedTime) > wait  && (millis() - startTime) < 1750)
  {
      previousLedTime = millis();
      if(!flashInit)
      {
        for(int i = 0; i < NUMPIXELS; i++)
        {
          strip1.setPixelColor(i, 0, 255, 0);
          strip2.setPixelColor(i, 0, 255, 0);
        }
        flashInit = true;
      }
      else
      {
        for(int i = 0; i < NUMPIXELS; i++)
        {
          strip1.setPixelColor(i, 0, 0, 0);
          strip2.setPixelColor(i, 0, 0, 0);
        }
        flashInit = false;
      }
      strip1.show();
      strip2.show();
  }
  else if((millis() - startTime) < duration)
  {
        for(int i = 0; i < NUMPIXELS; i++)
        {
          strip1.setPixelColor(i, 0, 255, 0);
          strip2.setPixelColor(i, 0, 255, 0);
        }
  }
  else
  {
    LEDinit = false;
    flashInit = false;
    ledPattern = 'a';
  }
}

void GlowRed(uint8_t wait)
{
  if((millis() - previousLedTime) > wait)
  {
    previousLedTime = millis();
    for (int j = 0; j < NUMPIXELS; j++)
    {
      if(glowBrightness < 127)
      {
        strip1.setPixelColor(j, glowBrightness, 0, 0);
        strip2.setPixelColor(j, glowBrightness, 0, 0);
      }
      else
      {
        strip1.setPixelColor(j, 255-glowBrightness, 0, 0);
        strip2.setPixelColor(j, 255-glowBrightness, 0, 0);
      }
    }
      strip1.show();
      strip2.show();
      glowBrightness++;
      glowBrightness %= 255;
  }
}
