"""Sensor platform for LubeLogger integration."""
from __future__ import annotations

from datetime import datetime
from typing import Any, cast

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import LubeLoggerDataUpdateCoordinator

SENSOR_TYPES = [
    {
        "key": "latest_odometer",
        "name": "Latest Odometer",
        "device_class": SensorDeviceClass.DISTANCE,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit": "mi",
        "value_path": "odometer",
    },
    {
        "key": "next_plan",
        "name": "Next Plan",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "value_path": ["dateCreated", "dateModified", "Date", "date"],
    },
    {
        "key": "latest_tax",
        "name": "Latest Tax",
        "device_class": SensorDeviceClass.MONETARY,
        "unit": "USD",
        "value_path": "cost",
    },
    {
        "key": "latest_service",
        "name": "Latest Service",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "value_path": ["date", "Date", "ServiceDate"],
    },
    {
        "key": "latest_repair",
        "name": "Latest Repair",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "value_path": ["date", "Date", "RepairDate"],
    },
    {
        "key": "latest_upgrade",
        "name": "Latest Upgrade",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "value_path": ["date", "Date", "UpgradeDate"],
    },
    {
        "key": "latest_supply",
        "name": "Latest Supply",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "value_path": ["date", "Date", "SupplyDate"],
    },
    {
        "key": "latest_gas",
        "name": "Latest Fuel Fill",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "value_path": ["date", "Date", "FuelDate"],
    },
    {
        "key": "next_reminder",
        "name": "Next Reminder",
        "device_class": SensorDeviceClass.TIMESTAMP,
        "value_path": ["dueDate", "DueDate", "Date", "date"],
    },
]

def parse_date(date_str: str | None) -> datetime | None:
    """Parse a date string from LubeLogger API and return timezone-aware datetime."""
    if not date_str:
        return None

    # Try ISO format first
    try:
        if date_str.endswith("Z"):
            date_str = date_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        # Ensure timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=dt_util.UTC)
        return dt
    except (ValueError, AttributeError):
        pass

    # Try common date formats, prioritizing DD/MM/YYYY then MM/DD/YYYY
    formats = [
        "%d/%m/%Y",  # Added: DD/MM/YYYY format
        "%d/%m/%Y %H:%M:%S", # Added: DD/MM/YYYY with time
        "%m/%d/%Y",  # LubeLogger format: "12/17/2025"
        "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # Make timezone-aware (assume local timezone)
            if dt.tzinfo is None:
                dt = dt_util.as_local(dt)
            return dt
        except (ValueError, AttributeError):
            continue

    return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up LubeLogger sensors from a config entry."""
    coordinator: LubeLoggerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors: list[SensorEntity] = []
    vehicles = coordinator.data.get("vehicles", [])

    for vehicle in vehicles:
        vehicle_id = vehicle.get("id")
        vehicle_name = vehicle.get("name", f"Vehicle {vehicle_id}")
        vehicle_info = vehicle.get("vehicle_info", {})

        for sensor_type in SENSOR_TYPES:
            if vehicle.get(sensor_type["key"]):
                sensors.append(
                    LubeLoggerSensor(
                        coordinator,
                        vehicle_id,
                        vehicle_name,
                        vehicle_info,
                        sensor_type,
                    )
                )

    async_add_entities(sensors)


class LubeLoggerSensor(CoordinatorEntity, SensorEntity):
    """A generic LubeLogger sensor."""

    def __init__(
        self,
        coordinator: LubeLoggerDataUpdateCoordinator,
        vehicle_id: int,
        vehicle_name: str,
        vehicle_info: dict,
        sensor_type: dict,
    ) -> None:
        super().__init__(coordinator)
        self._vehicle_id = vehicle_id
        self._vehicle_name = vehicle_name
        self._vehicle_info = vehicle_info
        self._sensor_type = sensor_type

        self._attr_name = f'{vehicle_name} {sensor_type["name"]}'
        self._attr_unique_id = f'lubelogger_{vehicle_id}_{sensor_type["key"]}'
        self._attr_device_class = sensor_type.get("device_class")
        self._attr_state_class = sensor_type.get("state_class")
        self._attr_native_unit_of_measurement = sensor_type.get("unit")

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info for the vehicle."""
        make = self._vehicle_info.get("Make") or self._vehicle_info.get("make") or ""
        model = self._vehicle_info.get("Model") or self._vehicle_info.get("model") or ""
        year = str(self._vehicle_info.get("Year") or self._vehicle_info.get("year") or "")
        
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._vehicle_id))},
            name=self._vehicle_name,
            manufacturer=make or "LubeLogger",
            model=model or self._vehicle_name,
            sw_version=year,
        )

    @property
    def _record(self) -> dict | None:
        data = self.coordinator.data or {}
        vehicles = data.get("vehicles", [])
        for vehicle in vehicles:
            if vehicle.get("id") == self._vehicle_id:
                rec = vehicle.get(self._sensor_type["key"])
                return rec if isinstance(rec, dict) else None
        return None

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        return self._record is not None

    @property
    def native_value(self) -> Any:
        rec = self._record
        if not rec:
            return None

        value_path = self._sensor_type["value_path"]
        if isinstance(value_path, list):
            for field in value_path:
                value = rec.get(field)
                if value:
                    break
        else:
            value = rec.get(value_path)

        if self.device_class == SensorDeviceClass.TIMESTAMP:
            return parse_date(cast(str, value))

        if self.device_class == SensorDeviceClass.DISTANCE:
            if rec.get("adjusted"):
                value = rec.get("odometer")
            else:
                value = rec.get("odometer") or rec.get("Odometer")

        if value:
            try:
                return int(value)
            except (ValueError, TypeError):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return value
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        return self._record or None
