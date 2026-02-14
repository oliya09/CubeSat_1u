/* communication.c - Communication Implementation */
#include "communication.h"

static uint8_t tx_buffer[UART_TX_BUFFER_SIZE];
static uint8_t rx_buffer[UART_RX_BUFFER_SIZE];
static uint16_t rx_index = 0;

HAL_StatusTypeDef COMM_Init(void) {
    /* Start reception */
    HAL_UART_Receive_IT(&huart1, rx_buffer, 1);
    return HAL_OK;
}

void COMM_ProcessReceivedData(uint8_t* data, uint16_t length) {
    static uint16_t expected_length = 0;
    static uint8_t packet_type = 0;
    
    for(uint16_t i = 0; i < length; i++) {
        rx_buffer[rx_index++] = data[i];
        
        /* Check for packet start */
        if(rx_index == 1 && rx_buffer[0] != 0xAA) {
            rx_index = 0;
            continue;
        }
        
        if(rx_index == 2) {
            if(rx_buffer[1] == 0x55) {
                packet_type = 0x01;  /* Telemetry */
                expected_length = sizeof(TelemetryPacket_t);
            } else if(rx_buffer[1] == 0x56) {
                packet_type = 0x02;  /* Command */
                expected_length = sizeof(CommandPacket_t);
            } else {
                rx_index = 0;
            }
        }
        
        /* Check if we have complete packet */
        if(rx_index >= expected_length && expected_length > 0) {
            if(packet_type == 0x02) {
                CommandPacket_t* cmd = (CommandPacket_t*)rx_buffer;
                osMessageQueuePut(commandQueueHandle, cmd, 0, 0);
            }
            rx_index = 0;
            expected_length = 0;
        }
    }
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    if(huart->Instance == USART1) {
        COMM_ProcessReceivedData(rx_buffer, 1);
        HAL_UART_Receive_IT(&huart1, rx_buffer, 1);
    }
}