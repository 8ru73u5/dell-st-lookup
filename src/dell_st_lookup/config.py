from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Any

import yaml

from dell_st_lookup import browser_profiles as bp

DriverType = Literal['chrome', 'edge', 'safari', 'firefox']

_driver_type_mappings: dict[DriverType, bp.BrowserProfile] = {
    'chrome': bp.CHROME_PROFILE,
    'edge': bp.EDGE_PROFILE,
    'firefox': bp.FIREFOX_PROFILE,
    'safari': bp.SAFARI_PROFILE
}

_required_config_keys = {'driver_type', 'driver_executable'}


@dataclass
class Config:
    driver_type: DriverType
    driver_executable: Path
    driver_options: list[str] = field(default_factory=list)
    database_path: Path | Literal[':memory:'] = ':memory:'

    @property
    def driver_init_function(self) -> bp.WebDriverType:
        return _driver_type_mappings[self.driver_type].init

    @property
    def driver_options_function(self) -> bp.OptionsType:
        return _driver_type_mappings[self.driver_type].options

    @property
    def driver_service_function(self) -> bp.ServiceType:
        return _driver_type_mappings[self.driver_type].service

    @staticmethod
    def parse_driver_type(driver_type: Any) -> DriverType:
        if not isinstance(driver_type, str):
            raise ValueError('driver_type should be a string value')

        if driver_type not in _driver_type_mappings:
            driver_type_text = ', '.join(_driver_type_mappings.keys())
            raise ValueError(f'driver_type should be one of the following: {driver_type_text}')

        return driver_type  # type: ignore

    @staticmethod
    def parse_driver_executable(driver_executable: Any) -> Path:
        if not isinstance(driver_executable, Path):
            try:
                driver_executable = Path(driver_executable)
            except TypeError:
                raise ValueError('driver_executable should be a valid file path')

        if not driver_executable.is_file():
            raise ValueError('driver_executable should be a valid file path')

        return driver_executable  # type: ignore

    @staticmethod
    def parse_driver_options(driver_options: Any) -> list[str]:
        if driver_options is None:
            return []

        if not isinstance(driver_options, list):
            raise ValueError('driver_options should be a list')

        for v in driver_options:
            if not isinstance(v, str):
                raise ValueError('driver_options should contain string values only')

        return driver_options  # type: ignore

    @staticmethod
    def parse_database_path(database_path: Any) -> Path | Literal[':memory:']:
        if database_path == ':memory:' or database_path is None:
            return ':memory:'

        if not isinstance(database_path, Path):
            try:
                database_path = Path(database_path)
            except TypeError:
                raise ValueError('database_path should be a valid file path')

        if not database_path.exists():
            return database_path  # type: ignore

        if not database_path.is_file():
            raise ValueError('database_path should be a valid file path')

        return database_path  # type: ignore

    @staticmethod
    def from_file(config_path: Path):
        try:
            with open(config_path) as f:
                config_file = yaml.safe_load(f.read())
        except (FileNotFoundError, IsADirectoryError):
            raise ValueError(f'Config path is not a valid file: {config_path}')

        if not isinstance(config_file, dict):
            raise ValueError('Invalid config file! Check config_example.yml for reference')

        if not _required_config_keys.issubset(config_file.keys()):
            required_values_text = ', '.join(_required_config_keys)
            raise ValueError(
                f'Config file does not include some of required values: {required_values_text}'
            )

        driver_type = Config.parse_driver_type(config_file['driver_type'])
        driver_executable = Config.parse_driver_executable(config_file['driver_executable'])
        driver_options = Config.parse_driver_options(config_file.get('driver_options'))
        database_path = Config.parse_database_path(config_file.get('database_path'))

        return Config(
            driver_type=driver_type,
            driver_executable=driver_executable,
            driver_options=driver_options,
            database_path=database_path
        )
