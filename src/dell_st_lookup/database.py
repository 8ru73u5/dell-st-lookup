import sqlite3
from datetime import datetime
from typing import Optional

from dell_st_lookup.config import Config
from dell_st_lookup.device import DellDevice


class DeviceCache:
    _DATE_FORMAT = '%d %b %Y'

    def __init__(self, config: Config) -> None:
        self.connection = sqlite3.Connection(config.database_path)
        self.connection.row_factory = sqlite3.Row
        self._init_database()

    def _init_database(self) -> None:
        query = '''
            CREATE TABLE IF NOT EXISTS devices (
                service_tag TEXT PRIMARY KEY,
                device_type TEXT,
                name TEXT,
                warranty_type TEXT,
                warranty_expiration_date TEXT
            );
        '''

        with self.connection:
            self.connection.execute(query)

    def get_device(self, service_tag: str) -> Optional[DellDevice]:
        cur = self.connection.cursor()

        query = 'SELECT * FROM devices WHERE service_tag = ?;'
        params = (service_tag.upper(),)
        cur.execute(query, params)

        device = cur.fetchone()
        if not device:
            return None

        expiration_date = datetime.strptime(device['warranty_expiration_date'], self._DATE_FORMAT)
        return DellDevice(
            device_type=device['device_type'],
            name=device['name'],
            service_tag=device['service_tag'],
            warranty_type=device['warranty_type'],
            warranty_expiration_date=expiration_date
        )

    def insert_device(self, device: DellDevice) -> None:
        query = '''
            INSERT INTO devices (
                service_tag, device_type, name, warranty_type, warranty_expiration_date
            ) VALUES (
                :service_tag, :device_type, :name, :warranty_type, :warranty_expiration_date
            ) ON CONFLICT DO NOTHING;
        '''

        params = ({
            'service_tag': device.service_tag.upper(),
            'device_type': device.device_type,
            'name': device.name,
            'warranty_type': device.warranty_type,
            'warranty_expiration_date': device.warranty_expiration_date.strftime(self._DATE_FORMAT)
        },)

        with self.connection:
            self.connection.executemany(query, params)

    def quit(self) -> None:
        self.connection.close()
