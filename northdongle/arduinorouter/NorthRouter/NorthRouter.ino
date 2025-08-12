/**
 * __  __ ____ _  __ ____ ___ __  __
 * \ \/ // __// |/ //  _// _ |\ \/ /
 *  \  // _/ /    /_/ / / __ | \  /
 *  /_//___//_/|_//___//_/ |_| /_/
 *
 * Yeniay Control Computer Firmware
 *
 * Copyright (C) 2022 Yeniay
 *
 * This program is free software: you
 * can redistribute it and/or modify it
 * under the terms of the GNU General
 * Public License as published by the
 * Free Software Foundation, in version 3.
 *
 * You should have received a copy of
 * the GNU General Public License along
 * with this program. If not, see
 * <http://www.gnu.org/licenses/>.
 */

#include <Arduino.h>
#include <SPI.h>
#include "RF24.h"
#include "ntrp.h"
#include "ntrp_router.h"

#ifdef ARDUINO_AVR_UNO
#define LEDPIN 13
RF24 rfmodule(8,9);
NTRP_Router router(&Serial,&rfmodule);
#define SERIAL_BEGIN Serial.begin
#endif

#ifdef _SAM_INCLUDED_
#define LEDPIN 14
RF24 rfmodule(A8,A9);
NTRP_Router router(&SerialUSB,&rfmodule);
#define SERIAL_BEGIN SerialUSB.begin
#endif


uint32_t counter = 0;
bool ledvalue = HIGH;

void setup() {
  pinMode(LEDPIN, OUTPUT);
  SERIAL_BEGIN(ROUTER_BAUD);

  /* Halt if NRF Module does not begin*/
  if(!rfmodule.begin()) while(1);
  rfmodule.setDataRate(RF24_2MBPS);
  rfmodule.setPALevel(RF24_PA_MAX);
  while(!router.sync(100)); 

  delay(100);
  router.debug("NTRP Router Start v.8");
}

void loop() {
  static NTRP_Message_t msg;
  NTRP_InitMessage(&msg);
  if(router.receiveMaster(&msg)){
    router.route(&msg);
    digitalWrite(LEDPIN, ledvalue);
    ledvalue = !ledvalue; 
  }
  NTRP_InitMessage(&msg);
  if(router.receivePipe(&msg)){
    router.route(&msg);
    digitalWrite(LEDPIN, ledvalue);
    ledvalue = !ledvalue; 
  }
}
