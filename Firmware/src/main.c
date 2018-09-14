/**************************************************************************//**
 * @file    main.c
 * @brief   Main routine for Oscilloscope Simulation System
 *
 * This firmware communicates with the Oscilloscope Simulation System Windows application
 *
 * @author  Silicon Laboratories
 *
 *******************************************************************************
 * @section License
 * (C) Copyright 2018 Silicon Labs Inc,
 * http://developer.silabs.com/legal/version/v11/Silicon_Labs_Software_License_Agreement.txt
 *
 ******************************************************************************
 *
 * This file is licensed under the Silabs License Agreement. See the file
 * "Silabs_License_Agreement.txt" for details. Before using this software for
 * any purpose, you must agree to the terms of that agreement.
 *
 ******************************************************************************/

// -----------------------------------------------------------------------------
// Includes

#include <SI_EFM8UB1_Register_Enums.h>                // SFR declarations
#include "bsp.h"
#include "InitDevice.h"
#include "efm8_usbxpress.h"
#include "descriptor.h"
#include <stdint.h>
#include <stdbool.h>
#include "protocol.h"
#include <string.h>
// -----------------------------------------------------------------------------
// Function Prototypes

void my_usbxp_callback(void);

void parseCommand(void);

// -----------------------------------------------------------------------------

/// Last packet received from host
SI_SEGMENT_VARIABLE(outPacket[USB_PACKET_SIZE], uint8_t, SI_SEG_XDATA);

/// Next packet to sent to host
SI_SEGMENT_VARIABLE(inPacket[USB_PACKET_SIZE], uint8_t, SI_SEG_XDATA);

// Buffer for store ADC value
SI_SEGMENT_VARIABLE(ADCP17Packet[USB_PACKET_SIZE], uint8_t, SI_SEG_XDATA);
SI_SEGMENT_VARIABLE(ADCP12Packet[USB_PACKET_SIZE], uint8_t, SI_SEG_XDATA);
SI_SEGMENT_VARIABLE(ADCdataPing[USB_PACKET_SIZE], uint8_t, SI_SEG_XDATA);
SI_SEGMENT_VARIABLE(ADCdataPong[USB_PACKET_SIZE], uint8_t, SI_SEG_XDATA);

/// Next packet to return state to host
SI_SEGMENT_VARIABLE(returnPacket[USB_MAX_PACKET_SIZE], uint8_t, SI_SEG_XDATA);

/// State of PB0
bool pb0State = false;

/// State of PB1
bool pb1State = false;

bool ADCP17Enable = false;

bool ADCP12Enable = false;

/// Current value of joystick
volatile uint32_t joystickValue;
volatile bool channel1ConvertComplete = false;
volatile bool channel2ConvertComplete = false;
volatile bool frequenceComplete = false;
volatile uint16_t sendADCAmount = 20;
volatile uint16_t countP17 = 0, countP12 = 0, iP17 = 0, iP12 = 0;
extern uint16_t writeLen;

// -----------------------------------------------------------------------------
// Functions

//-----------------------------------------------------------------------------
// SiLabs_Startup() Routine
// ----------------------------------------------------------------------------
// This function is called immediately after reset, before the initialization
// code is run in SILABS_STARTUP.A51 (which runs before main() ). This is a
// useful place to disable the watchdog timer, which is enable by default
// and may trigger before main() in some instances.
//-----------------------------------------------------------------------------
void SiLabs_Startup (void)
{
  // Disable the watchdog here
}
 
/**************************************************************************//**
 * @brief Main loop
 *
 * The main loop sets up the device and then waits forever. All active tasks
 * are ISR driven.
 *
 *****************************************************************************/
void main(void)
{
  //uint8_t portSave;

  enter_DefaultMode_from_RESET();

  USBX_init(&initStruct);
  USBX_apiCallbackEnable(my_usbxp_callback);

  BSP_LED_B = BSP_LED_OFF;
  BSP_LED_G = BSP_LED_OFF;
  BSP_LED_R = BSP_LED_OFF;
  memset(ADCP17Packet, 0, strlen(ADCP17Packet));
  memset(ADCdataPing, 0, strlen(ADCdataPing));

  memset(ADCP12Packet, 0, strlen(ADCP17Packet));
  memset(ADCdataPong, 0, strlen(ADCdataPing));

  // Enable global interrupts
  IE_EA = 1;

  // Spin forever
  while (1)
  {
	if(channel1ConvertComplete)
	{
		channel1ConvertComplete = false;

		ADCdataPing[START_BYTE] = PREAMBLE;       // start
		ADCdataPing[COMMAND_BYTE] = CHANNEL1_VALUE;       // adc value return
		ADCdataPing[LENGTH_BYTE] = sendADCAmount * 2;    // adc value byte amount

		USBX_blockWrite(ADCdataPing, sendADCAmount * 2 + 3, &writeLen);
	}
	if(channel2ConvertComplete)
		{
			channel2ConvertComplete = false;

			ADCdataPong[START_BYTE] = PREAMBLE;       // start
			ADCdataPong[COMMAND_BYTE] = CHANNEL2_VALUE;       // adc value return
			ADCdataPong[LENGTH_BYTE] = sendADCAmount * 2;    // adc value byte amount
			USBX_blockWrite(ADCdataPong, sendADCAmount * 2 + 3, &writeLen);
		}
	if(frequenceComplete)
	{
		frequenceComplete = false;
		USBX_blockWrite(returnPacket, 4, &writeLen);
	}
  }
}


// -------------------------------
// Interrupt Service Routines

/**************************************************************************//**
 * @brief USBXpress call-back
 *
 * This function is called by USBXpress.
 *
 *****************************************************************************/
void my_usbxp_callback(void)
{
   uint16_t readLen;
   uint32_t intval = USBX_getCallbackSource();
   uint8_t SFRPAGE_save = SFRPAGE;
   SFRPAGE = LEGACY_PAGE;

   // Device Opened
   if (intval & USBX_DEV_OPEN)
   {

	  // Read data from host.
     USBX_blockRead(outPacket, USB_PACKET_SIZE, &readLen);
   }

   // Device Closed or Suspended
   if (intval & (USBX_DEV_CLOSE | USBX_DEV_SUSPEND))
   {
     // Stop Timer 3 to disable ADC convert.
     TMR3CN0 &= ~TMR3CN0_TR3__RUN;

     // If entering suspend, call USBX_suspend() to enter low-power mode
     if (intval & USBX_DEV_SUSPEND)
     {
       USBX_suspend();
     }
   }

   // USB Read complete
   if (intval & USBX_RX_COMPLETE)
   {
	 parseCommand();
     USBX_blockRead(outPacket, USB_PACKET_SIZE, &readLen);
   }

   // USB write complete
   if (intval & USBX_TX_COMPLETE)
   {

   }
   SFRPAGE = SFRPAGE_save;
}

/************************************************************************//**
 * @brief Parse the commands
 * Parse the commands from host.
 ****************************************************************************/
void parseCommand(void)
{
	uint8_t command;
	uint8_t high,low;
	uint16_t n,f;
	command = outPacket[COMMAND_BYTE];
	switch(command)
	{
	  case ENABLE_CHANNEL:
		  if(outPacket[VALUE_BYTE0] == CHANNEL1)
		  {
			  if(outPacket[VALUE_BYTE1] == 0x01)
			  {
				  BSP_LED_R = BSP_LED_ON;
				  ADCP17Enable = true;
			  	  ADC0MX = ADC0MX_ADC0MX__ADC0P15;
			  }
			  else
			  {
				  BSP_LED_R = BSP_LED_OFF;
				  ADCP17Enable = false;
				  if(ADCP12Enable == true)
				  {
					  ADC0MX = ADC0MX_ADC0MX__ADC0P10;
				  }
				  else
				  {
					  ADC0MX = ADC0MX_ADC0MX__NONE;
				  }
			  }
		  }
		  else if (outPacket[VALUE_BYTE0] == CHANNEL2)
		  {

			  if(outPacket[VALUE_BYTE1] == 0x01)
			  {
				  BSP_LED_B = BSP_LED_ON;
				  ADCP12Enable = true;
			  	  ADC0MX = ADC0MX_ADC0MX__ADC0P10;
			  }
			  else
			  {
				  BSP_LED_B = BSP_LED_OFF;
				  ADCP12Enable = false;
				  if(ADCP17Enable == true)
				  {
					  ADC0MX = ADC0MX_ADC0MX__ADC0P15;
				  }
				  else
				  {
					  ADC0MX = ADC0MX_ADC0MX__NONE;
				  }
			  }
		  }
		  else
		  {
			  BSP_LED_G = BSP_LED_ON;
		  }
		  break;
	  case ENABLE_ADC:
	  		  if(outPacket[VALUE_BYTE0])
	  		  {
	  			  TMR3CN0 |= TMR3CN0_TR3__RUN;
	  		  }
	  		  else
	  		  {
	  			  TMR3CN0 &= ~TMR3CN0_TR3__RUN;
	  		  }
	  		  break;
	  case LED_GET:
		  returnPacket[0] = 0xFE;
		  returnPacket[1] = 0x02;
		  returnPacket[2] = LED_STATE;
		  if(0x01 == outPacket[VALUE_BYTE0])
		  {
			  returnPacket[3] = 0x01;
			  returnPacket[4] =	(BSP_LED_R == BSP_LED_ON)? 0x01 : 0x00;
		  	  USBX_blockWrite(returnPacket, USB_MAX_PACKET_SIZE, &writeLen);
		  }
		  else if(0x02 == outPacket[VALUE_BYTE0])
		  {
			  returnPacket[3] = 0x02;
			  returnPacket[4] =	(BSP_LED_G == BSP_LED_ON)? 0x01 : 0x00;
			  USBX_blockWrite(returnPacket, USB_MAX_PACKET_SIZE, &writeLen);
		  }
		  else if(0x03 == outPacket[VALUE_BYTE0])
		  {
			  returnPacket[3] = 0x03;
			  returnPacket[4] =	(BSP_LED_B == BSP_LED_ON)? 0x01 : 0x00;
			  USBX_blockWrite(returnPacket, USB_MAX_PACKET_SIZE, &writeLen);
		  }
		  else
		  {
			  returnPacket[3] = 0x00;
			  returnPacket[4] =	0x00;
			  USBX_blockWrite(returnPacket, USB_MAX_PACKET_SIZE, &writeLen);
		  }
		  break;

	  case LED_SET:
		  if(0x01 == outPacket[VALUE_BYTE0])
		  {
			  BSP_LED_R = (outPacket[VALUE_BYTE1] == 0x01) ? BSP_LED_ON : BSP_LED_OFF;
		  }
		  else if(0x02 == outPacket[VALUE_BYTE0])
		  {
			  BSP_LED_G = (outPacket[VALUE_BYTE1] == 0x01) ? BSP_LED_ON : BSP_LED_OFF;
		  }
		  else if(0x03 == outPacket[VALUE_BYTE0])
		  {
			  BSP_LED_B = (outPacket[VALUE_BYTE1] == 0x01) ? BSP_LED_ON : BSP_LED_OFF;
		  }
		  else
		  {

		  }
		  break;

	  case GPIO_GET:
		  break;
	  case GPIO_SET:
		  break;
	  case FRENQUENCY_GET:

		  returnPacket[START_BYTE] = 0xAA;
		  returnPacket[LENGTH_BYTE] = 0x01;
		  returnPacket[COMMAND_BYTE] = FRENQUENCE_STATE;
		  n = TMR3RLH;
		  n = n << 8;
		  n += TMR3RLL;
		  if(ADCP17Enable && ADCP12Enable)
		  {
			  f = 10000/(65536-n)/2;
		  }
		  else
		  {
			  f = 10000/(65536-n);
		  }
		  if(f == 1000)
		  {
			  returnPacket[VALUE_BYTE0] = FREQUENCY_1000HZ;
		  }
		  else if(f==100)
		  {
			  returnPacket[VALUE_BYTE0] = FREQUENCY_100HZ;
		  }
		  else if(f==10)
		  {
		  	  returnPacket[VALUE_BYTE0] = FREQUENCY_10HZ;
		  }
		  else if(f==4)
		  {
		  	  returnPacket[VALUE_BYTE0] = FREQUENCY_4HZ;
		  }
		  else
		  {
			  returnPacket[VALUE_BYTE0] = FREQUENCY_UNKNOW;
		  }
		  frequenceComplete = true;
		  break;
	  case FRENQUENCY_SET:

		  //0x03:1KHZ, 0x02:100Hz, 0x01:10Hz, 0x00:4Hz
		  if(0x03 == outPacket[VALUE_BYTE0])
		  {
			  if(ADCP17Enable&&ADCP12Enable)
			  {
				  //65531
				  high = 0xFF;
				  low = 0xFB;
			  }
			  else
			  {
				  //65526
				  high = 0xFF;
				  low = 0xF6;
			  }
		  }
		  else if(0x02 == outPacket[VALUE_BYTE0])
		  {
			  if(ADCP17Enable&&ADCP12Enable)
			  {
				  //65486
				  high = 0xFF;
				  low = 0xCE;
			  }
			  else
			  {
				  //65436
				  high = 0xFF;
				  low = 0x9C;
			  }
		  }
		  else if(0x01 == outPacket[VALUE_BYTE0])
		  {
			  if(ADCP17Enable&&ADCP12Enable)
			  {
				  //65036
				  high = 0xFE;
				  low = 0x0C;
			  }
			  else
			  {
				  //64536
				  high = 0xFC;
				  low = 0x18;
			  }
		  }
		  else if(0x00 == outPacket[VALUE_BYTE0])
		  {
			  if(ADCP17Enable&&ADCP12Enable)
			  {
				  //64286
				  high = 0xFB;
				  low = 0x1E;
			  }
			  else
			  {
				  //63036
				  high = 0xF6;
				  low = 0x3C;
			  }
		  }
		  else
		  {
			  return;
		  }
		  TMR3RLH = (high << TMR3RLH_TMR3RLH__SHIFT);
		  TMR3RLL = (low << TMR3RLL_TMR3RLL__SHIFT);
		  break;
	  case ACCURACY_GET:
		  break;
	  case ACCURACY_SET:
		  break;
	  default:
		  break;
	}
}
