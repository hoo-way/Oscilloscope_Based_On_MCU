//=========================================================
// src/Interrupts.c: generated by Hardware Configurator
//
// This file will be regenerated when saving a document.
// leave the sections inside the "$[...]" comment tags alone
// or they will be overwritten!
//=========================================================

// -----------------------------------------------------------------------------
// Includes

#include <SI_EFM8UB1_Register_Enums.h>
#include "bsp.h"
#include "descriptor.h"
#include "joystick.h"
#include <string.h>

// -----------------------------------------------------------------------------
// Constants

// -------------------------------
// Temperature Sensor Coefficients

#define SCALE       1000L   // Scale for temp calculations
#define SLOPE       2262    // Slope of the temp transfer function
#define OFFSET      265614L // Offset for the temp transfer function
#define OVER_ROUND  10      // Number of shifts (>>N) to reach the
                            // correct number of bits of precision

// -------------------------------
// Switch Locations

#define P0_PB0_BITMASK 0x04
#define P0_PB1_BITMASK 0x08

// -----------------------------------------------------------------------------
// Variables
extern volatile bool channel1ConvertComplete;
extern volatile bool channel2ConvertComplete;
extern volatile uint16_t sendADCAmount;
extern bool ADCP17Enable;
extern bool ADCP12Enable;
uint16_t writeLen;

// -----------------------------------------------------------------------------
// Extern Variables

extern volatile uint32_t joystickValue;
extern bool pb0State;
extern bool pb1State;
extern volatile uint16_t countP17, iP17;
extern volatile uint16_t countP12, iP12;
// Buffer for store ADC value
extern SI_SEGMENT_VARIABLE(ADCP17Packet[USB_PACKET_SIZE], uint8_t, SI_SEG_XDATA);
extern SI_SEGMENT_VARIABLE(ADCdataPing[USB_PACKET_SIZE], uint8_t, SI_SEG_XDATA);
extern SI_SEGMENT_VARIABLE(ADCP12Packet[USB_PACKET_SIZE], uint8_t, SI_SEG_XDATA);
extern SI_SEGMENT_VARIABLE(ADCdataPong[USB_PACKET_SIZE], uint8_t, SI_SEG_XDATA);
// -----------------------------------------------------------------------------

// -----------------------------------------------------------------------------
// Functions

//-----------------------------------------------------------------------------
// TIMER3_ISR
//-----------------------------------------------------------------------------
//
// TIMER3 ISR Content goes here. Remember to clear flag bits:
// TMR3CN0::TF3H (Timer # High Byte Overflow Flag)
// TMR3CN0::TF3L (Timer # Low Byte Overflow Flag)
//
//-----------------------------------------------------------------------------
SI_INTERRUPT (TIMER3_ISR, TIMER3_IRQn)
{
  uint8_t SFRPAGE_save = SFRPAGE;
  SFRPAGE = TIMER3_PAGE;

  // High byte overflow
  if (TMR3CN0 & TMR3CN0_TF3H__SET)
  {
    TMR3CN0 &= ~ TMR3CN0_TF3H__SET;
  }

  SFRPAGE = SFRPAGE_save;
}

//-----------------------------------------------------------------------------
// PMATCH_ISR
//-----------------------------------------------------------------------------
//
// PMATCH ISR Content goes here. Remember to clear flag bits:
//
//-----------------------------------------------------------------------------
SI_INTERRUPT (PMATCH_ISR, PMATCH_IRQn)
{
  uint8_t SFRPAGE_save = SFRPAGE;
  SFRPAGE = LEGACY_PAGE;

  // PB0
  if ((P0 & P0_PB0_BITMASK) ^ (P0MAT & P0_PB0_BITMASK))
  {
    if (BSP_PB0)
    {
      P0MAT |= P0_PB0_BITMASK;
    }
    else
    {
      // At this point, PB0 has been pressed and released.
      // Toggle pb0State
      pb0State = ~pb0State;
      P0MAT &= ~P0_PB0_BITMASK;

    }
  }
  // PB1
  else if ((P0 & P0_PB1_BITMASK) ^ (P0MAT & P0_PB1_BITMASK))
  {
    if (BSP_PB1)
    {
      P0MAT |= P0_PB1_BITMASK;
    }
    else
    {
      // At this point, PB1 has been pressed and released.
      // Toggle pb1State
      pb1State = ~pb1State;
      P0MAT &= ~P0_PB1_BITMASK;
    }
  }

  SFRPAGE = SFRPAGE_save;
}

//-----------------------------------------------------------------------------
// ADC0EOC_ISR
//-----------------------------------------------------------------------------
//
// ADC0EOC ISR Content goes here. Remember to clear flag bits:
// ADC0CN0::ADINT (Conversion Complete Interrupt Flag)
//
//-----------------------------------------------------------------------------
SI_INTERRUPT (ADC0EOC_ISR, ADC0EOC_IRQn)
{
  uint16_t sample_P17,sample_P12;
  uint8_t SFRPAGE_save = SFRPAGE;
  SFRPAGE = LEGACY_PAGE;
  if (ADC0MX == ADC0MX_ADC0MX__ADC0P15)
  {
	  sample_P17 = ADC0;
	  joystickValue = ((uint32_t)sample_P17) * 3300 / 1024;

	  ADCP17Packet[iP17] = joystickValue >> 8;  // ADCdataPing High-byte Value
	  ADCP17Packet[iP17+1] = joystickValue & 0x00ff;    // ADCdataPing0 Low-byte value
	  countP17 += 1;
	  iP17 += 2;
	  if(countP17 >= sendADCAmount)
	  {
		  channel1ConvertComplete = true;
		  countP17 = 0;
		  iP17 = 0;
		  strncpy(ADCdataPing+3, ADCP17Packet, sendADCAmount * 2);
		  memset(ADCP17Packet, 0, strlen(ADCP17Packet));

	  }
	  if(ADCP12Enable)
	  {
		  ADC0MX = ADC0MX_ADC0MX__ADC0P10;
	  }
  }
  else
  {
	  sample_P12 = ADC0;
	  sample_P12 = ((uint32_t)sample_P12) * 3300 / 1024;

	  ADCP12Packet[iP12] = sample_P12 >> 8;  // ADCdataPing High-byte Value
	  ADCP12Packet[iP12+1] = sample_P12 & 0x00ff;    // ADCdataPing0 Low-byte value
	  countP12 += 1;
	  iP12 += 2;
	  if(countP12 >= sendADCAmount)
	  {
		  channel2ConvertComplete = true;
		  countP12 = 0;
		  iP12 = 0;
		  strncpy(ADCdataPong+3, ADCP12Packet, sendADCAmount * 2);
		  memset(ADCP12Packet, 0, strlen(ADCP12Packet));
	  }
	  if(ADCP17Enable)
	  {
		  ADC0MX = ADC0MX_ADC0MX__ADC0P15;
	  }
  }

  ADC0CN0_ADINT = 0;
  SFRPAGE = SFRPAGE_save;
}

