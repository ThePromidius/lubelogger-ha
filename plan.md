# Plan de Refactorización y Nuevas Funcionalidades de LubeLogger

## Análisis del Código Actual

1.  **Falta de Agrupación de Dispositivos:** El problema principal es la ausencia de una propiedad `device_info` en las clases de sensores. Esto impide que Home Assistant agrupe los sensores (odómetro, impuestos, etc.) bajo un único dispositivo por vehículo.
2.  **Código Repetitivo:** Existe una duplicación significativa de código en la definición y registro de cada tipo de sensor. La lógica es casi idéntica para todos los sensores.
3.  **Coordinador Sólido:** El `DataUpdateCoordinator` (`LubeLoggerDataUpdateCoordinator`) está bien implementado para obtener y manejar los datos de la API de LubeLogger.
4.  **API de Solo Lectura:** El cliente actual (`LubeLoggerClient`) está diseñado principalmente para obtener datos (GET requests). Para añadir registros, necesitaremos implementar funcionalidades POST.

## Plan de Refactorización y Nuevas Funcionalidades

### Fase 1: Refactorización Existente (agrupación de dispositivos y centralización de sensores)

1.  **Implementar `device_info`:**
    *   Se agregará una propiedad `@property` llamada `device_info` a la clase base `BaseLubeLoggerSensor`.
    *   Esta propiedad devolverá un diccionario con la información del vehículo (identificadores, nombre, modelo, etc.), lo que permitirá a Home Assistant asociar cada sensor con su vehículo correspondiente.

2.  **Centralizar la Creación de Sensores:**
    *   Se creará una función para generar dinámicamente las clases de sensores en lugar de mantener una lista estática.
    *   Esto eliminará el código repetitivo y simplificará la adición de nuevos sensores en el futuro.

3.  **Actualizar `async_setup_entry`:**
    *   Se modificará la función `async_setup_entry` para que utilice la nueva función de creación de sensores.
    *   Se asegurará de que los sensores generados dinámicamente se registren correctamente en Home Assistant.

### Fase 2: Implementación de Entrada de Combustible

1.  **Investigación de la API de LubeLogger para escritura:**
    *   **Confirmar el endpoint y el formato para añadir registros de combustible.** Se asumirá que existe un endpoint POST `/api/GasRecord` o similar. Si no se encuentra, se adaptará el plan.
    *   Identificar los campos necesarios para un registro de combustible (e.g., `vehicleId`, `odometer`, `fuelAmount`, `price`, `date`, `notes`, `isFullTank`).

2.  **Extensión del Cliente de LubeLogger (`client.py`):**
    *   Añadir una nueva función asíncrona, `async_add_gas_record(self, vehicle_id: int, data: dict)`, que realizará una solicitud POST al endpoint `/api/GasRecord` con los datos proporcionados.

3.  **Desarrollo del Servicio de Home Assistant (`__init__.py` y `services.yaml`):**
    *   Crear un nuevo servicio en el dominio `lubelogger` (e.g., `lubelogger.add_fuel_record`).
    *   Este servicio aceptará los parámetros necesarios del usuario (e.g., `vehicle_id`, `odometer`, `fuel_amount`, `price`, `date`, `notes`, `is_full_tank`).
    *   La implementación del servicio utilizará `LubeLoggerClient.async_add_gas_record` para enviar los datos a la API de LubeLogger.
    *   Después de una adición exitosa, se llamará a `coordinator.async_request_refresh()` para actualizar inmediatamente los sensores relacionados con el combustible en Home Assistant.
    *   Definir el esquema del servicio en `services.yaml` para una mejor integración en la UI de Home Assistant y validación.

4.  **Diseño de la Tarjeta de la Interfaz de Usuario (Lovelace):**
    *   Crear un ejemplo de tarjeta Lovelace (`lovelace_card_example.md`) que permita al usuario ingresar los datos de combustible y activar el servicio `lubelogger.add_fuel_record`.
    *   La tarjeta incluirá campos de entrada para:
        *   ID del vehículo (o selección si se puede inferir/manejar múltiples)
        *   Odómetro actual
        *   Cantidad de combustible (litros/galones)
        *   Precio por unidad
        *   Costo total (calculado o ingresado)
        *   Fecha del registro (por defecto, hoy)
        *   Notas opcionales
        *   Tanque lleno (checkbox)
    *   Un botón para ejecutar el servicio.

## Consideraciones Adicionales

*   **Manejo de Errores:** Implementar un manejo robusto de errores tanto en el cliente como en el servicio de Home Assistant para informar al usuario sobre fallos en la comunicación con la API de LubeLogger o datos inválidos.
*   **Localización:** Asegurarse de que los mensajes de error y las descripciones del servicio sean localizables.
*   **Validación:** Añadir validación de entrada para los campos del servicio para evitar enviar datos incorrectos a la API.
*   **Selección de Vehículo:** Para un UX óptimo, considerar cómo el usuario seleccionará el vehículo al que se le añade el registro de combustible, especialmente si hay múltiples vehículos configurados. Inicialmente, se puede requerir el `vehicle_id` como un parámetro explícito.
