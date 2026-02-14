// stm32f4xx_hal.h - Dummy HAL header for compilation
#ifndef __STM32F4XX_HAL_H
#define __STM32F4XX_HAL_H

#include <stdint.h>

// Basic HAL types
typedef enum {
    HAL_OK       = 0x00,
    HAL_ERROR    = 0x01,
    HAL_BUSY     = 0x02,
    HAL_TIMEOUT  = 0x03
} HAL_StatusTypeDef;

typedef enum {
    HAL_UNLOCKED = 0x00,
    HAL_LOCKED   = 0x01
} HAL_LockTypeDef;

// GPIO typedefs
typedef struct {
    uint32_t Pin;
    uint32_t Mode;
    uint32_t Pull;
    uint32_t Speed;
    uint32_t Alternate;
} GPIO_InitTypeDef;

#define GPIO_PIN_0   ((uint16_t)0x0001)
#define GPIO_PIN_1   ((uint16_t)0x0002)
#define GPIO_PIN_13  ((uint16_t)0x2000)

#define GPIO_MODE_OUTPUT_PP 0x00000001
#define GPIO_MODE_IT_RISING 0x10100
#define GPIO_NOPULL         0x00000000
#define GPIO_PULLDOWN       0x00000002
#define GPIO_SPEED_FREQ_LOW 0x00000000

// UART typedefs
typedef struct {
    uint32_t BaudRate;
    uint32_t WordLength;
    uint32_t StopBits;
    uint32_t Parity;
    uint32_t Mode;
    uint32_t HwFlowCtl;
    uint32_t OverSampling;
    uint32_t Instance;
} UART_InitTypeDef;

typedef struct {
    uint32_t Instance;
    UART_InitTypeDef Init;
    uint8_t* pTxBuffPtr;
    uint16_t TxXferSize;
    uint16_t TxXferCount;
    uint8_t* pRxBuffPtr;
    uint16_t RxXferSize;
    uint16_t RxXferCount;
    void* hdmatx;
    void* hdmarx;
    HAL_LockTypeDef Lock;
    uint32_t ErrorCode;
} UART_HandleTypeDef;

#define UART_WORDLENGTH_8B 0x00000000
#define UART_STOPBITS_1    0x00000000
#define UART_PARITY_NONE   0x00000000
#define UART_MODE_TX_RX    0x00000003
#define UART_HWCONTROL_NONE 0x00000000
#define UART_OVERSAMPLING_16 0x00000000

#define USART1 ((uint32_t)1)

// I2C typedefs
typedef struct {
    uint32_t ClockSpeed;
    uint32_t DutyCycle;
    uint32_t OwnAddress1;
    uint32_t AddressingMode;
    uint32_t DualAddressMode;
    uint32_t OwnAddress2;
    uint32_t GeneralCallMode;
    uint32_t NoStretchMode;
} I2C_InitTypeDef;

typedef struct {
    uint32_t Instance;
    I2C_InitTypeDef Init;
    uint8_t* pBuffPtr;
    uint16_t XferSize;
    uint16_t XferCount;
    void* hdmatx;
    void* hdmarx;
    HAL_LockTypeDef Lock;
    uint32_t ErrorCode;
} I2C_HandleTypeDef;

#define I2C_DUTYCYCLE_2 0x00000000
#define I2C_ADDRESSINGMODE_7BIT 0x00000001
#define I2C_DUALADDRESS_DISABLE 0x00000000
#define I2C_GENERALCALL_DISABLE 0x00000000
#define I2C_NOSTRETCH_DISABLE 0x00000000
#define I2C_MEMADD_SIZE_8BIT 0x00000001

// SPI typedefs
typedef struct {
    uint32_t Mode;
    uint32_t Direction;
    uint32_t DataSize;
    uint32_t CLKPolarity;
    uint32_t CLKPhase;
    uint32_t NSS;
    uint32_t BaudRatePrescaler;
    uint32_t FirstBit;
    uint32_t TIMode;
    uint32_t CRCCalculation;
    uint32_t CRCPolynomial;
} SPI_InitTypeDef;

typedef struct {
    uint32_t Instance;
    SPI_InitTypeDef Init;
    uint8_t* pTxBuffPtr;
    uint16_t TxXferSize;
    uint16_t TxXferCount;
    uint8_t* pRxBuffPtr;
    uint16_t RxXferSize;
    uint16_t RxXferCount;
    void* hdmatx;
    void* hdmarx;
    HAL_LockTypeDef Lock;
    uint32_t ErrorCode;
} SPI_HandleTypeDef;

#define SPI_MODE_MASTER 0x00000104
#define SPI_DIRECTION_2LINES 0x00000000
#define SPI_DATASIZE_8BIT 0x00000000
#define SPI_POLARITY_LOW 0x00000000
#define SPI_PHASE_1EDGE 0x00000000
#define SPI_NSS_SOFT 0x00000200
#define SPI_BAUDRATEPRESCALER_16 0x00000038
#define SPI_FIRSTBIT_MSB 0x00000000
#define SPI_TIMODE_DISABLE 0x00000000
#define SPI_CRCCALCULATION_DISABLE 0x00000000

// ADC typedefs
typedef struct {
    uint32_t ClockPrescaler;
    uint32_t Resolution;
    uint32_t ScanConvMode;
    uint32_t ContinuousConvMode;
    uint32_t DiscontinuousConvMode;
    uint32_t ExternalTrigConvEdge;
    uint32_t DataAlign;
    uint32_t NbrOfConversion;
    uint32_t DMAContinuousRequests;
    uint32_t EOCSelection;
} ADC_InitTypeDef;

typedef struct {
    uint32_t Instance;
    ADC_InitTypeDef Init;
    uint32_t Channel;
    HAL_LockTypeDef Lock;
    uint32_t ErrorCode;
} ADC_HandleTypeDef;

typedef struct {
    uint32_t Channel;
    uint32_t Rank;
    uint32_t SamplingTime;
} ADC_ChannelConfTypeDef;

#define ADC_CLOCK_SYNC_PCLK_DIV4 0x00000000
#define ADC_RESOLUTION_12B 0x00000000
#define DISABLE 0
#define ENABLE 1
#define ADC_CHANNEL_0 0
#define ADC_SAMPLETIME_3CYCLES 0

// IWDG typedefs
typedef struct {
    uint32_t Prescaler;
    uint32_t Reload;
} IWDG_InitTypeDef;

typedef struct {
    uint32_t Instance;
    IWDG_InitTypeDef Init;
} IWDG_HandleTypeDef;

#define IWDG_PRESCALER_64 0x00000004

// CMSIS OS typedefs
typedef void* osThreadId_t;
typedef void* osMessageQueueId_t;
typedef void* osTimerId_t;
typedef uint32_t TickType_t;
typedef void (*osThreadFunc_t)(void *);

#define osThreadNew(func, arg, attr) (osThreadId_t)1
#define osMessageQueueNew(count, size, attr) (osMessageQueueId_t)1
#define osMessageQueuePut(queue, msg, priority, timeout) 0
#define osMessageQueueGet(queue, msg, priority, timeout) 0
#define osKernelInitialize() 0
#define osKernelStart() 0
#define osDelay(ms) ((void)0)
#define xTaskGetTickCount() 0
#define vTaskDelayUntil(prev, ticks) ((void)0)
#define pdMS_TO_TICKS(ms) (ms)
#define taskENTER_CRITICAL() ((void)0)
#define taskEXIT_CRITICAL() ((void)0)

// RCC functions
void HAL_RCC_OscConfig(void* cfg) { (void)cfg; }
void HAL_RCC_ClockConfig(void* cfg, uint32_t latency) { (void)cfg; (void)latency; }

#define RCC_OSCILLATORTYPE_HSE 0x00000001
#define RCC_HSE_ON 0x00000001
#define RCC_PLL_ON 0x02000000
#define RCC_PLLSOURCE_HSE 0x00010000
#define RCC_PLLP_DIV2 0x00000002
#define RCC_CLOCKTYPE_SYSCLK 0x00000001
#define RCC_CLOCKTYPE_HCLK 0x00000004
#define RCC_CLOCKTYPE_PCLK1 0x00000008
#define RCC_CLOCKTYPE_PCLK2 0x00000010
#define RCC_SYSCLKSOURCE_PLLCLK 0x00000002
#define RCC_SYSCLK_DIV1 0x00000000
#define RCC_HCLK_DIV2 0x00000400
#define FLASH_LATENCY_2 0x00000002

// HAL functions
void HAL_Init(void) {}
uint32_t HAL_GetTick(void) { return 0; }
void HAL_Delay(uint32_t ms) { (void)ms; }
void HAL_GPIO_Init(void* port, void* pin) {}
void HAL_GPIO_WritePin(void* port, uint16_t pin, uint8_t state) {}
void HAL_GPIO_TogglePin(void* port, uint16_t pin) {}
void HAL_NVIC_SetPriority(uint32_t irq, uint32_t prio, uint32_t sub) {}
void HAL_NVIC_EnableIRQ(uint32_t irq) {}
void HAL_GPIO_EXTI_IRQHandler(uint16_t pin) {}
void HAL_GPIO_EXTI_Callback(uint16_t pin) {}

// HAL status
#define HAL_MAX_DELAY 0xFFFFFFFF

#endif // __STM32F4XX_HAL_H