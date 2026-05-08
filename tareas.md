# Tareas para la Implementación de Entrada de Combustible en LubeLogger

Este documento detalla las tareas necesarias para implementar la funcionalidad de añadir registros de combustible a través de Home Assistant, siguiendo el `plan.md`.

## Fase 1: Refactorización Existente (agrupación de dispositivos y centralización de sensores)

*   **Tarea 1.1: Modificar `BaseLubeLoggerSensor` para `device_info`**
    *   **Archivo:** `custom_components/lubelogger/sensor.py`
    *   **Descripción:** Añadir la propiedad `@property device_info` a la clase `BaseLubeLoggerSensor`. Esta propiedad debe devolver un diccionario con `identifiers`, `name`, `model`, y `manufacturer` utilizando los datos del vehículo.
    *   **Estimación:** 2 horas

*   **Tarea 1.2: Centralizar la Creación de Sensores**
    *   **Archivo:** `custom_components/lubelogger/sensor.py`
    *   **Descripción:** Crear una función (e.g., `_create_lubelogger_sensors`) que acepte el `coordinator`, `entity_description`, y el `vehicle` como parámetros y devuelva una lista de objetos de sensor. Esto reemplazará la definición individual de cada sensor.
    *   **Estimación:** 3 horas

*   **Tarea 1.3: Actualizar `async_setup_entry`**
    *   **Archivo:** `custom_components/lubelogger/__init__.py`
    *   **Descripción:** Modificar `async_setup_entry` para usar la función centralizada de creación de sensores (Tarea 1.2) para registrar todos los sensores asociados a cada vehículo.
    *   **Estimación:** 2 horas

*   **Tarea 1.4: Pruebas de Refactorización**
    *   **Descripción:** Verificar que todos los sensores existentes sigan funcionando correctamente y que estén agrupados bajo sus respectivos vehículos en la interfaz de Home Assistant.
    *   **Estimación:** 2 horas

## Fase 2: Implementación de Entrada de Combustible

*   **Tarea 2.1: Investigación de la API de LubeLogger (POST para GasRecord)**
    *   **Descripción:** Confirmar el endpoint exacto para añadir registros de combustible (ej. `/api/GasRecord`). Identificar los campos JSON requeridos (`vehicleId`, `odometer`, `fuelAmount`, `price`, `date`, `notes`, `isFullTank`, etc.). Si no hay documentación clara, se requerirá experimentación o suposición informada.
    *   **Estimación:** 1-2 horas (dependiendo de la documentación disponible)

*   **Tarea 2.2: Extensión del Cliente de LubeLogger (`client.py`)**
    *   **Archivo:** `custom_components/lubelogger/client.py`
    *   **Descripción:** Añadir una nueva función `async_add_gas_record(self, vehicle_id: int, data: dict)` que realice una solicitud POST al endpoint de la API de LubeLogger para añadir un registro de combustible. La función debe manejar la serialización de `data` a JSON.
    *   **Estimación:** 3 horas

*   **Tarea 2.3: Desarrollo del Servicio de Home Assistant (`__init__.py`)**
    *   **Archivo:** `custom_components/lubelogger/__init__.py`
    *   **Descripción:** Implementar una función para el servicio de Home Assistant (e.g., `handle_add_fuel_record`). Esta función recuperará el `LubeLoggerClient` del coordinador, extraerá los datos del `call.data`, y llamará a `client.async_add_gas_record`. Después de una adición exitosa, debe llamar a `coordinator.async_request_refresh()`.
    *   **Estimación:** 4 horas

*   **Tarea 2.4: Definición del Esquema del Servicio (`services.yaml`)**
    *   **Archivo:** `custom_components/lubelogger/services.yaml`
    *   **Descripción:** Crear o actualizar el archivo `services.yaml` para definir el esquema del nuevo servicio `add_fuel_record`. Esto incluirá la descripción, los campos esperados (`vehicle_id`, `odometer`, `fuel_amount`, `price`, `date`, `notes`, `is_full_tank`), y sus tipos.
    *   **Estimación:** 1 hora

*   **Tarea 2.5: Pruebas del Servicio**
    *   **Descripción:** Probar el nuevo servicio utilizando las herramientas de desarrollo de Home Assistant para asegurar que los registros se añaden correctamente a LubeLogger y que los sensores se actualizan.
    *   **Estimación:** 2 horas

## Fase 3: Diseño y Ejemplo de Tarjeta Lovelace

*   **Tarea 3.1: Crear Ejemplo de Tarjeta Lovelace**
    *   **Archivo:** `lovelace_card_example.md` (o similar)
    *   **Descripción:** Diseñar un ejemplo de configuración de tarjeta Lovelace que utilice componentes de entrada (e.g., `input_number`, `input_text`, `input_datetime`, `input_boolean`) para recopilar los datos del registro de combustible y un botón para activar el servicio `lubelogger.add_fuel_record`.
    *   **Estimación:** 3 horas

## Total Estimado:
~23-24 horas