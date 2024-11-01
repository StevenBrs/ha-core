"""The Backup integration."""

import voluptuous as vol

from homeassistant.components.hassio import is_hassio
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DATA_MANAGER, DOMAIN, LOGGER
from .http import async_register_http_views
from .manager import BackupManager
from .websocket import async_register_websocket_handlers

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)

SERVICE_CREATE_SCHEMA = vol.Schema({vol.Optional(CONF_PASSWORD): str})


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Backup integration."""
    backup_manager = BackupManager(hass)
    hass.data[DATA_MANAGER] = backup_manager

    with_hassio = is_hassio(hass)

    async_register_websocket_handlers(hass, with_hassio)

    if with_hassio:
        if DOMAIN in config:
            LOGGER.error(
                "The backup integration is not supported on this installation method, "
                "please remove it from your configuration"
            )
        return True

    async def async_handle_create_service(call: ServiceCall) -> None:
        """Service handler for creating backups."""
        await backup_manager.async_create_backup(password=call.data.get(CONF_PASSWORD))

    hass.services.async_register(
        DOMAIN,
        "create",
        async_handle_create_service,
        schema=SERVICE_CREATE_SCHEMA,
    )

    async_register_http_views(hass)

    return True
