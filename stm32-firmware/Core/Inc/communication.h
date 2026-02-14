/* communication.h - Communication Header */
#ifndef __COMMUNICATION_H
#define __COMMUNICATION_H

#include "main.h"

/* UART Buffers */
#define UART_TX_BUFFER_SIZE 512
#define UART_RX_BUFFER_SIZE 256

/* Protocol Constants */
#define SYNC_TELEMETRY   0xAA55
#define SYNC_COMMAND     0xAA56
#define SYNC_IMAGE       0xAA58
#define SYNC_FILE        0xAA59

/* Communication Functions */
HAL_StatusTypeDef COMM_Init(void);
HAL_StatusTypeDef COMM_SendTelemetry(TelemetryPacket_t* packet);
HAL_StatusTypeDef COMM_SendData(uint8_t* data, uint16_t length, uint16_t sync_word);
void COMM_ProcessReceivedData(uint8_t* data, uint16_t length);
void COMM_StartReception(void);

/* UART Callbacks */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart);
void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart);

/* Beacon Functions */
void COMM_SendBeacon(void);
void COMM_SetBeaconInterval(uint32_t seconds);

#endif /* __COMMUNICATION_H */