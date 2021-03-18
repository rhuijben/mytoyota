"""Base classes"""
import logging
from typing import Optional

_LOGGER: logging.Logger = logging.getLogger(__package__)


class Vehicle:  # pylint: disable=too-many-instance-attributes
    """Class to hold car information for each car"""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        vehicle_info: Optional[dict],
        connected_services: Optional[dict],
        odometer: Optional[list],
        parking: Optional[dict],
        status: Optional[dict],
    ) -> None:
        self.odometer = None
        self.parking = None
        self.battery = None
        self.hvac = None
        self.alias = vehicle_info["alias"] if "alias" in vehicle_info else None
        self.vin = vehicle_info["vin"] if "vin" in vehicle_info else None

        # If no vehicle information is provided, abort.
        if not vehicle_info:
            _LOGGER.error("No vehicle information provided")
            return

        # Format vehicle information.
        self.details = self.format_details(vehicle_info)

        # Checks if connected services has been enabled.
        if self.has_connected_services_enabled(connected_services):

            # Extract odometer information.
            if odometer:
                self.odometer = self.format_odometer(odometer)

            # Extract parking information.
            if parking:
                self.parking = parking

            # Extracts information from status.
            if status:
                self.extract_status(status)

    def __str__(self) -> str:
        return str(self.as_dict())

    def as_dict(self) -> dict:
        """Return car information in dict"""
        return {
            "alias": self.alias,
            "vin": self.vin,
            "details": self.details,
            "status": {
                "battery": self.battery,
                "hvac": self.hvac,
                "odometer": self.odometer,
                "parking": self.parking,
            },
        }

    def extract_status(self, status) -> None:
        """Extract information like battery and hvac from status."""
        if "VehicleInfo" in status:
            if "RemoteHvacInfo" in status["VehicleInfo"]:
                self.hvac = status["VehicleInfo"]["RemoteHvacInfo"]

            if "ChargeInfo" in status["VehicleInfo"]:
                self.battery = status["VehicleInfo"]["ChargeInfo"]

    def has_connected_services_enabled(self, json_dict) -> bool:
        """Checks if the user has enabled connected services."""
        if (
            "connectedServices" in json_dict
            and json_dict["connectedServices"]["status"] == "ACTIVATED"
        ):
            return True

        _LOGGER.error("Please setup Connected Services for this car. (%s)", self.vin)
        return False

    @staticmethod
    def format_odometer(raw) -> dict:
        """Formats odometer information from a list to a dict."""
        instruments = {}
        for instrument in sorted(raw):
            instruments[instrument["type"]] = instrument["value"]
            if "unit" in instrument:
                instruments[instrument["type"] + "_unit"] = instrument["unit"]

        return instruments

    @staticmethod
    def format_details(raw) -> dict:
        """Formats vehicle info into a dict."""
        details = {}
        for item in sorted(raw):
            if item in ("vin", "alias"):
                continue
            details[item] = raw[item]
        return details
