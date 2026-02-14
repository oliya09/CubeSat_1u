/* sensors.c - Sensor Implementation */
#include "sensors.h"

/* BME280 Calibration Data */
static struct {
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
    uint16_t dig_P1;
    int16_t  dig_P2;
    int16_t  dig_P3;
    int16_t  dig_P4;
    int16_t  dig_P5;
    int16_t  dig_P6;
    int16_t  dig_P7;
    int16_t  dig_P8;
    int16_t  dig_P9;
    uint8_t  dig_H1;
    int16_t  dig_H2;
    uint8_t  dig_H3;
    int16_t  dig_H4;
    int16_t  dig_H5;
    int8_t   dig_H6;
} bme280_cal;

HAL_StatusTypeDef Sensors_Init(void) {
    /* Read BME280 calibration data */
    uint8_t cal_data[32];
    
    if(HAL_I2C_Mem_Read(&hi2c1, BME280_ADDR, 0x88, I2C_MEMADD_SIZE_8BIT, 
                         cal_data, 24, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    
    /* Parse calibration data */
    bme280_cal.dig_T1 = (uint16_t)(cal_data[1] << 8 | cal_data[0]);
    bme280_cal.dig_T2 = (int16_t)(cal_data[3] << 8 | cal_data[2]);
    bme280_cal.dig_T3 = (int16_t)(cal_data[5] << 8 | cal_data[4]);
    
    bme280_cal.dig_P1 = (uint16_t)(cal_data[7] << 8 | cal_data[6]);
    bme280_cal.dig_P2 = (int16_t)(cal_data[9] << 8 | cal_data[8]);
    bme280_cal.dig_P3 = (int16_t)(cal_data[11] << 8 | cal_data[10]);
    bme280_cal.dig_P4 = (int16_t)(cal_data[13] << 8 | cal_data[12]);
    bme280_cal.dig_P5 = (int16_t)(cal_data[15] << 8 | cal_data[14]);
    bme280_cal.dig_P6 = (int16_t)(cal_data[17] << 8 | cal_data[16]);
    bme280_cal.dig_P7 = (int16_t)(cal_data[19] << 8 | cal_data[18]);
    bme280_cal.dig_P8 = (int16_t)(cal_data[21] << 8 | cal_data[20]);
    bme280_cal.dig_P9 = (int16_t)(cal_data[23] << 8 | cal_data[22]);
    
    /* Read humidity calibration */
    HAL_I2C_Mem_Read(&hi2c1, BME280_ADDR, 0xA1, I2C_MEMADD_SIZE_8BIT, 
                     &bme280_cal.dig_H1, 1, HAL_MAX_DELAY);
    
    HAL_I2C_Mem_Read(&hi2c1, BME280_ADDR, 0xE1, I2C_MEMADD_SIZE_8BIT, 
                     cal_data, 7, HAL_MAX_DELAY);
    
    bme280_cal.dig_H2 = (int16_t)(cal_data[1] << 8 | cal_data[0]);
    bme280_cal.dig_H3 = cal_data[2];
    bme280_cal.dig_H4 = (int16_t)((cal_data[3] << 4) | (cal_data[4] & 0x0F));
    bme280_cal.dig_H5 = (int16_t)((cal_data[5] << 4) | (cal_data[4] >> 4));
    bme280_cal.dig_H6 = (int8_t)cal_data[6];
    
    return HAL_OK;
}