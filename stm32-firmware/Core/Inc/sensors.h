/* sensors.h - Sensor Drivers Header */
#ifndef __SENSORS_H
#define __SENSORS_H

#include "main.h"

/* Sensor Initialization */
HAL_StatusTypeDef Sensors_Init(void);

/* LIS3MDL Magnetometer */
HAL_StatusTypeDef LIS3MDL_Init(void);
HAL_StatusTypeDef LIS3MDL_Read(float* mx, float* my, float* mz);

/* BME280 Environmental Sensor */
HAL_StatusTypeDef BME280_Init(void);
HAL_StatusTypeDef BME280_Read(float* temp, float* press, float* hum);
float BME280_CompensateTemperature(int32_t raw_temp);
float BME280_CompensatePressure(int32_t raw_press);
float BME280_CompensateHumidity(int32_t raw_hum);

/* TMP117 Precision Temperature */
HAL_StatusTypeDef TMP117_Init(void);
HAL_StatusTypeDef TMP117_Read(float* temp);

/* MCP3008 ADC (SPI) */
uint16_t MCP3008_Read(uint8_t channel);

/* Battery Monitoring */
uint16_t Read_Battery_Voltage(void);
uint16_t Read_Battery_Current(void);

/* Radiation Counter */
uint32_t Get_Radiation_Counts(void);
void Reset_Radiation_Counter(void);

#endif /* __SENSORS_H */