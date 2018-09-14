/**************************************************************************//**
 * @file    protocol.h
 * @brief   External constant declarations for protocol.c
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
#ifndef __PROTOCOL_H__
#define __PROTOCOL_H__

#define USB_MAX_PACKET_SIZE 10

enum COMMAND{
		PREAMBLE = 0xaa,
		ENABLE_CHANNEL = 0xf1,
		ENABLE_ADC = 0xf2,
		ADC_GET = 0x01,
		CHANNEL1_VALUE = 0x02,
		CHANNEL2_VALUE = 0x03,
		LED_GET = 0X11,
		LED_STATE = 0X12,
		LED_SET = 0X13,
		GPIO_GET = 0X21,
		GPIO_STATE = 0X22,
		GPIO_SET = 0X23,
		BUTTON_EVENT = 0X31,
		FRENQUENCY_GET = 0X41,
		FRENQUENCE_STATE = 0X42,
		FRENQUENCY_SET = 0X43,
		ACCURACY_GET = 0X51,
		ACCURACY_STATE = 0X52,
		ACCURACY_SET = 0X53,

};

enum BYTE_SEQUENCE{
	START_BYTE = 0,
	COMMAND_BYTE,
	LENGTH_BYTE,
	VALUE_BYTE0,
	VALUE_BYTE1,
};

enum FREQUENCY{
	FREQUENCY_4HZ = 0x00,
	FREQUENCY_10HZ = 0x01,
	FREQUENCY_100HZ = 0x02,
	FREQUENCY_1000HZ = 0x03,
	FREQUENCY_UNKNOW = 0xFF,
};

enum CHANNEL{
	CHANNEL1 = 0x01, //P1.7
	CHANNEL2 = 0x02,  //P1.2
};

#endif //__PROTOCOL_H__
