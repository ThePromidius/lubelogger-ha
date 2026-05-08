# Plan de Refactorización de LubeLogger

## Análisis del Código Actual

1.  **Falta de Agrupación de Dispositivos:** El problema principal es la ausencia de una propiedad `device_info` en las clases de sensores. Esto impide que Home Assistant agrupe los sensores (odómetro, impuestos, etc.) bajo un único dispositivo por vehículo.
2.  **Código Repetitivo:** Existe una duplicación significativa de código en la definición y registro de cada tipo de sensor. La lógica es casi idéntica para todos los sensores.
3.  **Coordinador Sólido:** El `DataUpdateCoordinator` (`LubeLoggerDataUpdateCoordinator`) está bien implementado para obtener y manejar los datos de la API de LubeLogger.

## Plan de Refactorización

1.  **Implementar `device_info`:**
    *   Se agregará una propiedad `@property` llamada `device_info` a la clase base `BaseLubeLoggerSensor`.
    *   Esta propiedad devolverá un diccionario con la información del vehículo (identificadores, nombre, modelo, etc.), lo que permitirá a Home Assistant asociar cada sensor con su vehículo correspondiente.

2.  **Centralizar la Creación de Sensores:**
    *   Se creará una función para generar dinámicamente las clases de sensores en lugar de mantener una lista estática.
    *   Esto eliminará el código repetitivo y simplificará la adición de nuevos sensores en el futuro.

3.  **Actualizar `async_setup_entry`:**
    *   Se modificará la función `async_setup_entry` para que utilice la nueva función de creación de sensores.
    *   Se asegurará de que los sensores generados dinámicamente se registren correctamente en Home Assistant.
