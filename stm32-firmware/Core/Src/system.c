/* system.c - System Management Implementation */
#include "system.h"

static uint32_t last_health_check = 0;
static uint8_t task_health[4] = {0};

void SYSTEM_Init(void) {
    boot_count++;
    
    /* Read from EEPROM if available */
    /* Increment boot counter */
}

void SYSTEM_CheckHealth(void) {
    uint32_t current_time = HAL_GetTick();
    
    if((current_time - last_health_check) > 60000) {  /* Check every minute */
        /* Check if tasks are responding */
        task_health[0] = (osThreadGetState(sensorTaskHandle) == osThreadRunning);
        task_health[1] = (osThreadGetState(radiationTaskHandle) == osThreadRunning);
        task_health[2] = (osThreadGetState(commTaskHandle) == osThreadRunning);
        task_health[3] = (osThreadGetState(watchdogTaskHandle) == osThreadRunning);
        
        last_health_check = current_time;
    }
}

uint8_t SYSTEM_CheckTaskHealth(void) {
    return (task_health[0] && task_health[1] && 
            task_health[2] && task_health[3]);
}

void SYSTEM_ResetSystem(void) {
    HAL_Delay(100);
    NVIC_SystemReset();
}