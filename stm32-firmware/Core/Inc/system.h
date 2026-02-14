/* system.h - System Management Header */
#ifndef __SYSTEM_H
#define __SYSTEM_H

#include "main.h"

/* System Initialization */
void SYSTEM_Init(void);
void SYSTEM_Process(void);

/* Power Management */
void SYSTEM_EnterLowPower(void);
void SYSTEM_ExitLowPower(void);
void SYSTEM_ShutdownPeripherals(void);
void SYSTEM_RestartPeripherals(void);

/* Watchdog Management */
void SYSTEM_RefreshWatchdog(void);
void SYSTEM_CheckHealth(void);

/* Error Handling */
void SYSTEM_HandleError(uint8_t error_code);
void SYSTEM_LogEvent(const char* event);

/* Task Management */
uint8_t SYSTEM_CheckTaskHealth(void);
void SYSTEM_ResetSystem(void);

#endif /* __SYSTEM_H */