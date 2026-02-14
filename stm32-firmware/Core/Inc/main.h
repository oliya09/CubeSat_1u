/* main.h - CubeSat 1U Main Header */
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

#include "stm32f4xx_hal.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/* System States */
#define STATE_BOOT          0x00
#define STATE_IDLE          0x01
#define STATE_NOMINAL       0x02
#define STATE_SAFE          0x03
#define STATE_LOW_POWER     0x04
#define STATE_EMERGENCY     0x05
#define STATE_IMAGE_CAPTURE 0x06
#define STATE_DATA_TX       0x07

/* Command IDs */
#define CMD_PING            0x01
#define CMD_GET_TELEMETRY   0x02
#define CMD_CAPTURE_IMAGE   0x03
#define CMD_SET_MODE        0x04
#define CMD_RESET           0x05
#define CMD_TRANSMIT_FILE   0x06
#define CMD_UPDATE_FIRMWARE 0x07
#define CMD_SET_SCHEDULE    0x08
#define CMD_BEACON          0x09

/* Error Codes */
#define ERROR_NONE          0x00
#define ERROR_I2C           0x01
#define ERROR_SPI           0x02
#define ERROR_UART          0x03
#define ERROR_ADC           0x04
#define ERROR_BATTERY       0x05
#define ERROR_TEMPERATURE   0x06
#define ERROR_TASK_HANG     0x07
#define ERROR_MEMORY        0x08

/* Battery Thresholds (mV) */
#define BATTERY_NOMINAL     3700
#define BATTERY_LOW         3500
#define BATTERY_CRITICAL    3400

/* I2C Addresses */
#define LIS3MDL_ADDR        0x1E  /* Magnetometer */
#define BME280_ADDR         0x76  /* Environmental sensor */
#define TMP117_ADDR         0x48  /* Precision temperature */
#define MCP3008_ADDR        0x00  /* ADC (SPI, not I2C) */

/* Pin Definitions */
#define RADIATION_PIN       GPIO_PIN_0
#define RADIATION_PORT      GPIOA
#define LED_PIN             GPIO_PIN_13
#define LED_PORT            GPIOC
#define ADC_PIN             GPIO_PIN_0
#define ADC_PORT            GPIOB
#define PI_WAKE_PIN         GPIO_PIN_1
#define PI_WAKE_PORT        GPIOA

/* Telemetry Packet Structure */
typedef struct __attribute__((packed)) {
    uint8_t  sync1;              /* 0xAA */
    uint8_t  sync2;              /* 0x55 */
    uint8_t  packet_type;         /* 0x01 = telemetry */
    uint16_t sequence_number;
    uint32_t timestamp;
    
    /* Sensor Data */
    float    mag_x;               /* Gauss */
    float    mag_y;
    float    mag_z;
    uint16_t corrosion_raw;       /* ADC value */
    uint32_t radiation_cps;       /* Counts per second */
    float    temperature_bme;      /* °C */
    float    pressure;             /* hPa */
    float    humidity;             /* %RH */
    float    temperature_tmp;      /* °C (precision) */
    
    /* GPS Data */
    int32_t  latitude;            /* 1e7 degrees */
    int32_t  longitude;           /* 1e7 degrees */
    int32_t  altitude;            /* mm */
    uint8_t  gps_quality;
    uint8_t  gps_satellites;
    
    /* System Status */
    uint16_t battery_voltage;     /* mV */
    uint16_t battery_current;      /* mA */
    uint8_t  boot_count;
    uint8_t  error_flags;
    uint8_t  system_state;
    uint32_t uptime;              /* seconds */
    
    uint16_t checksum;
} TelemetryPacket_t;

/* Command Packet Structure */
typedef struct __attribute__((packed)) {
    uint8_t  sync1;              /* 0xAA */
    uint8_t  sync2;              /* 0x56 */
    uint8_t  command_id;
    uint16_t sequence_number;
    uint16_t parameter_length;
    uint8_t  parameters[64];
    uint16_t checksum;
} CommandPacket_t;

/* Function Prototypes */
void SystemClock_Config(void);
void Error_Handler(void);
uint16_t CalculateChecksum(void* data, uint16_t length);
void ProcessCommand(CommandPacket_t* cmd);
void LogError(uint8_t error_code);
void SendBeacon(void);
void ShutdownPayload(void);

extern uint8_t system_state;
extern TelemetryPacket_t current_telemetry;

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */