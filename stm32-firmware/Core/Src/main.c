/* main.c - STM32 Firmware */
#include "main.h"
#include "sensors.h"
#include "communication.h"
#include "system.h"
#include "cmsis_os.h"

/* Global Variables */
UART_HandleTypeDef huart1;  /* Communication with Pi */
UART_HandleTypeDef huart2;  /* Communication with Radio */
I2C_HandleTypeDef hi2c1;    /* I2C for sensors */
SPI_HandleTypeDef hspi1;    /* SPI for ADC */
ADC_HandleTypeDef hadc1;    /* ADC for battery */
IWDG_HandleTypeDef hiwdg;    /* Independent Watchdog */

/* FreeRTOS Handles */
osThreadId_t sensorTaskHandle;
osThreadId_t radiationTaskHandle;
osThreadId_t commTaskHandle;
osThreadId_t watchdogTaskHandle;
osMessageQueueId_t telemetryQueueHandle;
osMessageQueueId_t commandQueueHandle;
osTimerId_t beaconTimerHandle;

/* System State */
uint8_t system_state = STATE_BOOT;
uint32_t boot_count = 0;
uint32_t system_uptime = 0;
TelemetryPacket_t current_telemetry;
volatile uint32_t radiation_pulse_count = 0;

/* ==================== SYSTEM INITIALIZATION ==================== */

void SystemClock_Config(void) {
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    /* Configure HSE oscillator */
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInitStruct.HSEState = RCC_HSE_ON;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInitStruct.PLL.PLLM = 8;
    RCC_OscInitStruct.PLL.PLLN = 336;
    RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
    RCC_OscInitStruct.PLL.PLLQ = 7;
    HAL_RCC_OscConfig(&RCC_OscInitStruct);

    /* Configure system clocks */
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK |
                                   RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
    HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2);
}

void MX_GPIO_Init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    /* Enable GPIO clocks */
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();

    /* Configure LED pin */
    GPIO_InitStruct.Pin = LED_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(LED_PORT, &GPIO_InitStruct);

    /* Configure radiation input pin with interrupt */
    GPIO_InitStruct.Pin = RADIATION_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
    GPIO_InitStruct.Pull = GPIO_PULLDOWN;
    HAL_GPIO_Init(RADIATION_PORT, &GPIO_InitStruct);

    /* Configure Pi wake pin */
    GPIO_InitStruct.Pin = PI_WAKE_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(PI_WAKE_PORT, &GPIO_InitStruct);

    /* Set interrupt priorities */
    HAL_NVIC_SetPriority(EXTI0_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI0_IRQn);
}

void MX_I2C1_Init(void) {
    hi2c1.Instance = I2C1;
    hi2c1.Init.ClockSpeed = 100000;
    hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
    hi2c1.Init.OwnAddress1 = 0;
    hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
    hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
    hi2c1.Init.OwnAddress2 = 0;
    hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
    hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
    HAL_I2C_Init(&hi2c1);
}

void MX_SPI1_Init(void) {
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
    hspi1.Init.NSS = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_16;
    hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
    hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
    hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
    hspi1.Init.CRCPolynomial = 10;
    HAL_SPI_Init(&hspi1);
}

void MX_USART1_UART_Init(void) {
    huart1.Instance = USART1;
    huart1.Init.BaudRate = 115200;
    huart1.Init.WordLength = UART_WORDLENGTH_8B;
    huart1.Init.StopBits = UART_STOPBITS_1;
    huart1.Init.Parity = UART_PARITY_NONE;
    huart1.Init.Mode = UART_MODE_TX_RX;
    huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart1.Init.OverSampling = UART_OVERSAMPLING_16;
    HAL_UART_Init(&huart1);
}

void MX_USART2_UART_Init(void) {
    huart2.Instance = USART2;
    huart2.Init.BaudRate = 115200;
    huart2.Init.WordLength = UART_WORDLENGTH_8B;
    huart2.Init.StopBits = UART_STOPBITS_1;
    huart2.Init.Parity = UART_PARITY_NONE;
    huart2.Init.Mode = UART_MODE_TX_RX;
    huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart2.Init.OverSampling = UART_OVERSAMPLING_16;
    HAL_UART_Init(&huart2);
}

void MX_ADC1_Init(void) {
    ADC_ChannelConfTypeDef sConfig = {0};

    hadc1.Instance = ADC1;
    hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;
    hadc1.Init.Resolution = ADC_RESOLUTION_12B;
    hadc1.Init.ScanConvMode = DISABLE;
    hadc1.Init.ContinuousConvMode = ENABLE;
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
    hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    hadc1.Init.NbrOfConversion = 1;
    hadc1.Init.DMAContinuousRequests = DISABLE;
    hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
    HAL_ADC_Init(&hadc1);

    sConfig.Channel = ADC_CHANNEL_0;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_3CYCLES;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);
}

void MX_IWDG_Init(void) {
    hiwdg.Instance = IWDG;
    hiwdg.Init.Prescaler = IWDG_PRESCALER_64;
    hiwdg.Init.Reload = 4095;
    HAL_IWDG_Init(&hiwdg);
}

/* ==================== INTERRUPT HANDLERS ==================== */

void EXTI0_IRQHandler(void) {
    HAL_GPIO_EXTI_IRQHandler(RADIATION_PIN);
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if(GPIO_Pin == RADIATION_PIN) {
        radiation_pulse_count++;
    }
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    static CommandPacket_t rx_cmd;
    
    if(huart->Instance == USART1) {
        /* Command received from Pi */
        osMessageQueuePut(commandQueueHandle, &rx_cmd, 0, 0);
        HAL_UART_Receive_IT(&huart1, (uint8_t*)&rx_cmd, sizeof(CommandPacket_t));
    }
}

/* ==================== SENSOR FUNCTIONS ==================== */

/* LIS3MDL Magnetometer */
HAL_StatusTypeDef LIS3MDL_Init(void) {
    uint8_t config = 0;
    
    /* Configure control register 1 */
    config = 0x70;  /* 155Hz, XY ultra-low-power mode */
    if(HAL_I2C_Mem_Write(&hi2c1, LIS3MDL_ADDR, 0x20, I2C_MEMADD_SIZE_8BIT, 
                         &config, 1, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    
    /* Configure control register 2 */
    config = 0x00;  /* ±4 gauss */
    if(HAL_I2C_Mem_Write(&hi2c1, LIS3MDL_ADDR, 0x21, I2C_MEMADD_SIZE_8BIT, 
                         &config, 1, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    
    /* Configure control register 3 */
    config = 0x00;  /* Continuous conversion mode */
    if(HAL_I2C_Mem_Write(&hi2c1, LIS3MDL_ADDR, 0x22, I2C_MEMADD_SIZE_8BIT, 
                         &config, 1, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    
    /* Configure control register 4 */
    config = 0x08;  /* MSB at lower address */
    if(HAL_I2C_Mem_Write(&hi2c1, LIS3MDL_ADDR, 0x23, I2C_MEMADD_SIZE_8BIT, 
                         &config, 1, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    
    return HAL_OK;
}

HAL_StatusTypeDef LIS3MDL_Read(float* mx, float* my, float* mz) {
    uint8_t data[6];
    int16_t raw_x, raw_y, raw_z;
    
    /* Read magnetometer data */
    if(HAL_I2C_Mem_Read(&hi2c1, LIS3MDL_ADDR, 0x28, I2C_MEMADD_SIZE_8BIT, 
                         data, 6, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    
    /* Convert to 16-bit values (little endian) */
    raw_x = (int16_t)(data[1] << 8 | data[0]);
    raw_y = (int16_t)(data[3] << 8 | data[2]);
    raw_z = (int16_t)(data[5] << 8 | data[4]);
    
    /* Convert to Gauss (sensitivity: 0.00016 per LSB for ±4 gauss) */
    *mx = raw_x * 0.00016f;
    *my = raw_y * 0.00016f;
    *mz = raw_z * 0.00016f;
    
    return HAL_OK;
}

/* BME280 Environmental Sensor */
HAL_StatusTypeDef BME280_Init(void) {
    uint8_t config = 0;
    
    /* Reset sensor */
    config = 0xB6;
    if(HAL_I2C_Mem_Write(&hi2c1, BME280_ADDR, 0xE0, I2C_MEMADD_SIZE_8BIT, 
                         &config, 1, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    HAL_Delay(10);
    
    /* Configure humidity control */
    config = 0x03;  /* Oversampling x2 */
    if(HAL_I2C_Mem_Write(&hi2c1, BME280_ADDR, 0xF2, I2C_MEMADD_SIZE_8BIT, 
                         &config, 1, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    
    /* Configure measurement control */
    config = 0x27;  /* Temp oversampling x2, Pressure oversampling x16, Normal mode */
    if(HAL_I2C_Mem_Write(&hi2c1, BME280_ADDR, 0xF4, I2C_MEMADD_SIZE_8BIT, 
                         &config, 1, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    
    /* Configure config register */
    config = 0xA0;  /* Standby 1000ms, filter off */
    if(HAL_I2C_Mem_Write(&hi2c1, BME280_ADDR, 0xF5, I2C_MEMADD_SIZE_8BIT, 
                         &config, 1, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    
    return HAL_OK;
}

HAL_StatusTypeDef BME280_Read(float* temp, float* press, float* hum) {
    uint8_t data[8];
    int32_t raw_temp, raw_press, raw_hum;
    
    /* Read pressure (0xF7) */
    if(HAL_I2C_Mem_Read(&hi2c1, BME280_ADDR, 0xF7, I2C_MEMADD_SIZE_8BIT, 
                         data, 8, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    
    /* Extract 20-bit values */
    raw_press = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4);
    raw_temp = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4);
    raw_hum = (data[6] << 8) | data[7];
    
    /* Compensate values */
    *temp = BME280_CompensateTemperature(raw_temp);
    *press = BME280_CompensatePressure(raw_press) / 100.0f;
    *hum = BME280_CompensateHumidity(raw_hum);
    
    return HAL_OK;
}

float BME280_CompensateTemperature(int32_t raw_temp) {
    /* Simplified compensation - real code would use calibration data */
    return raw_temp / 100.0f;
}

float BME280_CompensatePressure(int32_t raw_press) {
    /* Simplified compensation */
    return raw_press / 256.0f;
}

float BME280_CompensateHumidity(int32_t raw_hum) {
    /* Simplified compensation */
    return raw_hum / 1024.0f;
}

/* TMP117 Precision Temperature */
HAL_StatusTypeDef TMP117_Init(void) {
    uint8_t config = 0;
    
    /* Read device ID to verify connection */
    if(HAL_I2C_Mem_Read(&hi2c1, TMP117_ADDR, 0x0F, I2C_MEMADD_SIZE_8BIT, 
                         &config, 1, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    
    /* Configure for continuous conversion */
    config = 0x00;
    if(HAL_I2C_Mem_Write(&hi2c1, TMP117_ADDR, 0x01, I2C_MEMADD_SIZE_8BIT, 
                         &config, 1, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    
    return HAL_OK;
}

HAL_StatusTypeDef TMP117_Read(float* temp) {
    uint8_t data[2];
    int16_t raw_temp;
    
    if(HAL_I2C_Mem_Read(&hi2c1, TMP117_ADDR, 0x00, I2C_MEMADD_SIZE_8BIT, 
                         data, 2, HAL_MAX_DELAY) != HAL_OK) {
        return HAL_ERROR;
    }
    
    raw_temp = (data[0] << 8) | data[1];
    *temp = raw_temp * 0.0078125f;  /* 7.8125 m°C per LSB */
    
    return HAL_OK;
}

/* MCP3008 ADC */
uint16_t MCP3008_Read(uint8_t channel) {
    uint8_t tx_data[3];
    uint8_t rx_data[3];
    
    /* Ensure channel is valid */
    channel &= 0x07;
    
    /* Build SPI command */
    tx_data[0] = 0x01;  /* Start bit */
    tx_data[1] = (0x80 | (channel << 4));  /* Single-ended + channel */
    tx_data[2] = 0x00;
    
    /* CS low */
    HAL_GPIO_WritePin(SPI1_CS_GPIO_Port, SPI1_CS_Pin, GPIO_PIN_RESET);
    
    /* SPI transaction */
    HAL_SPI_TransmitReceive(&hspi1, tx_data, rx_data, 3, HAL_MAX_DELAY);
    
    /* CS high */
    HAL_GPIO_WritePin(SPI1_CS_GPIO_Port, SPI1_CS_Pin, GPIO_PIN_SET);
    
    /* Extract 10-bit result */
    return ((rx_data[1] & 0x03) << 8) | rx_data[2];
}

/* Battery Monitoring */
uint16_t Read_Battery_Voltage(void) {
    uint32_t adc_value;
    uint16_t voltage_mv;
    
    HAL_ADC_Start(&hadc1);
    if(HAL_ADC_PollForConversion(&hadc1, 100) == HAL_OK) {
        adc_value = HAL_ADC_GetValue(&hadc1);
        /* Convert ADC (12-bit, 0-4095) to voltage (mV) */
        /* Voltage divider: 1:2, Vref = 3300mV */
        voltage_mv = (adc_value * 3300 * 2) / 4096;
        return voltage_mv;
    }
    HAL_ADC_Stop(&hadc1);
    
    return 0;
}

uint16_t Read_Battery_Current(void) {
    /* Would need current sensor - placeholder */
    return 0;
}

/* Radiation Counter */
uint32_t Get_Radiation_Counts(void) {
    uint32_t counts;
    
    taskENTER_CRITICAL();
    counts = radiation_pulse_count;
    taskEXIT_CRITICAL();
    
    return counts;
}

void Reset_Radiation_Counter(void) {
    taskENTER_CRITICAL();
    radiation_pulse_count = 0;
    taskEXIT_CRITICAL();
}

/* ==================== COMMUNICATION FUNCTIONS ==================== */

uint16_t CalculateChecksum(void* data, uint16_t length) {
    uint16_t checksum = 0;
    uint8_t* bytes = (uint8_t*)data;
    
    for(uint16_t i = 0; i < length; i++) {
        checksum += bytes[i];
    }
    
    return ~checksum;
}

HAL_StatusTypeDef COMM_SendTelemetry(TelemetryPacket_t* packet) {
    packet->sync1 = 0xAA;
    packet->sync2 = 0x55;
    packet->packet_type = 0x01;
    packet->timestamp = HAL_GetTick();
    packet->checksum = CalculateChecksum(packet, sizeof(TelemetryPacket_t) - 2);
    
    return HAL_UART_Transmit(&huart1, (uint8_t*)packet, 
                             sizeof(TelemetryPacket_t), HAL_MAX_DELAY);
}

void COMM_SendBeacon(void) {
    uint8_t beacon[] = {0xAA, 0x59, system_state, 
                        (uint8_t)(boot_count & 0xFF), 
                        (uint8_t)(current_telemetry.battery_voltage >> 8),
                        (uint8_t)(current_telemetry.battery_voltage & 0xFF)};
    
    HAL_UART_Transmit(&huart2, beacon, sizeof(beacon), HAL_MAX_DELAY);
}

void ProcessCommand(CommandPacket_t* cmd) {
    if(cmd->sync1 != 0xAA || cmd->sync2 != 0x56) {
        return;  /* Invalid sync */
    }
    
    uint16_t calc_checksum = CalculateChecksum(cmd, sizeof(CommandPacket_t) - 2);
    if(calc_checksum != cmd->checksum) {
        LogError(ERROR_UART);
        return;  /* Checksum error */
    }
    
    switch(cmd->command_id) {
        case CMD_PING:
        {
            uint8_t response[] = {0xAA, 0x57, 0x01, cmd->sequence_number & 0xFF};
            HAL_UART_Transmit(&huart1, response, 4, HAL_MAX_DELAY);
            break;
        }
        
        case CMD_GET_TELEMETRY:
            COMM_SendTelemetry(&current_telemetry);
            break;
            
        case CMD_CAPTURE_IMAGE:
            /* Wake Pi and request image */
            HAL_GPIO_WritePin(PI_WAKE_PORT, PI_WAKE_PIN, GPIO_PIN_SET);
            osDelay(100);
            HAL_GPIO_WritePin(PI_WAKE_PORT, PI_WAKE_PIN, GPIO_PIN_RESET);
            system_state = STATE_IMAGE_CAPTURE;
            break;
            
        case CMD_SET_MODE:
            if(cmd->parameter_length >= 1) {
                system_state = cmd->parameters[0];
            }
            break;
            
        case CMD_RESET:
            HAL_Delay(100);
            NVIC_SystemReset();
            break;
            
        case CMD_TRANSMIT_FILE:
            /* Forward to Pi */
            HAL_UART_Transmit(&huart1, (uint8_t*)cmd, 
                             sizeof(CommandPacket_t), HAL_MAX_DELAY);
            break;
            
        default:
            LogError(ERROR_UNKNOWN_COMMAND);
            break;
    }
}

void LogError(uint8_t error_code) {
    current_telemetry.error_flags |= error_code;
}

/* ==================== FreeRTOS TASKS ==================== */

void SensorTask(void *argument) {
    TickType_t lastWakeTime = xTaskGetTickCount();
    static uint16_t sequence = 0;
    
    /* Initialize sensors */
    LIS3MDL_Init();
    BME280_Init();
    TMP117_Init();
    
    while(1) {
        /* Read magnetometer */
        LIS3MDL_Read(&current_telemetry.mag_x, 
                     &current_telemetry.mag_y, 
                     &current_telemetry.mag_z);
        
        /* Read environmental sensors */
        BME280_Read(&current_telemetry.temperature_bme,
                    &current_telemetry.pressure,
                    &current_telemetry.humidity);
        
        TMP117_Read(&current_telemetry.temperature_tmp);
        
        /* Read corrosion sensor */
        current_telemetry.corrosion_raw = MCP3008_Read(0);
        
        /* Read battery */
        current_telemetry.battery_voltage = Read_Battery_Voltage();
        current_telemetry.battery_current = Read_Battery_Current();
        
        /* Update system info */
        current_telemetry.sequence_number = sequence++;
        current_telemetry.boot_count = boot_count;
        current_telemetry.system_state = system_state;
        current_telemetry.uptime = system_uptime;
        
        /* Send to queue */
        osMessageQueuePut(telemetryQueueHandle, &current_telemetry, 0, 0);
        
        /* Toggle LED */
        HAL_GPIO_TogglePin(LED_PORT, LED_PIN);
        
        /* Wait 1 second */
        vTaskDelayUntil(&lastWakeTime, pdMS_TO_TICKS(1000));
    }
}

void RadiationTask(void *argument) {
    uint32_t last_count = 0;
    uint32_t current_count;
    
    while(1) {
        /* Calculate counts per second */
        current_count = Get_Radiation_Counts();
        current_telemetry.radiation_cps = current_count - last_count;
        last_count = current_count;
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void CommTask(void *argument) {
    TelemetryPacket_t tx_packet;
    CommandPacket_t cmd;
    uint32_t last_beacon = 0;
    
    /* Start UART reception */
    HAL_UART_Receive_IT(&huart1, (uint8_t*)&cmd, sizeof(CommandPacket_t));
    
    while(1) {
        /* Send telemetry to Pi if available */
        if(osMessageQueueGet(telemetryQueueHandle, &tx_packet, 0, 10) == osOK) {
            COMM_SendTelemetry(&tx_packet);
        }
        
        /* Process commands */
        if(osMessageQueueGet(commandQueueHandle, &cmd, 0, 10) == osOK) {
            ProcessCommand(&cmd);
        }
        
        /* Send beacon every 30 seconds */
        if((HAL_GetTick() - last_beacon) > 30000 && 
           (system_state == STATE_NOMINAL || system_state == STATE_IDLE)) {
            COMM_SendBeacon();
            last_beacon = HAL_GetTick();
        }
        
        osDelay(100);
    }
}

void WatchdogTask(void *argument) {
    while(1) {
        /* Check system health */
        if(current_telemetry.battery_voltage < BATTERY_CRITICAL) {
            system_state = STATE_LOW_POWER;
            ShutdownPayload();
        }
        
        if(current_telemetry.temperature_bme > 70.0f || 
           current_telemetry.temperature_bme < -20.0f) {
            system_state = STATE_SAFE;
            LogError(ERROR_TEMPERATURE);
        }
        
        /* Refresh watchdog */
        HAL_IWDG_Refresh(&hiwdg);
        
        /* Increment uptime (every 5 seconds) */
        system_uptime += 5;
        
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}

void ShutdownPayload(void) {
    /* Put Pi to sleep */
    HAL_GPIO_WritePin(PI_WAKE_PORT, PI_WAKE_PIN, GPIO_PIN_RESET);
    
    /* Disable non-essential peripherals */
    __HAL_RCC_I2C1_CLK_DISABLE();
    __HAL_RCC_SPI1_CLK_DISABLE();
}

/* ==================== MAIN ==================== */

int main(void) {
    /* HAL Init */
    HAL_Init();
    
    /* Configure system clock */
    SystemClock_Config();
    
    /* Initialize peripherals */
    MX_GPIO_Init();
    MX_I2C1_Init();
    MX_SPI1_Init();
    MX_USART1_UART_Init();
    MX_USART2_UART_Init();
    MX_ADC1_Init();
    MX_IWDG_Init();
    
    /* Initialize kernel */
    osKernelInitialize();
    
    /* Create queues */
    telemetryQueueHandle = osMessageQueueNew(10, sizeof(TelemetryPacket_t), NULL);
    commandQueueHandle = osMessageQueueNew(5, sizeof(CommandPacket_t), NULL);
    
    /* Create tasks */
    osThreadNew(SensorTask, NULL, NULL);
    osThreadNew(RadiationTask, NULL, NULL);
    osThreadNew(CommTask, NULL, NULL);
    osThreadNew(WatchdogTask, NULL, NULL);
    
    /* Start scheduler */
    osKernelStart();
    
    /* Should never reach here */
    while(1) {
        HAL_IWDG_Refresh(&hiwdg);
    }
}

void Error_Handler(void) {
    while(1) {
        HAL_GPIO_TogglePin(LED_PORT, LED_PIN);
        HAL_Delay(100);
    }
}