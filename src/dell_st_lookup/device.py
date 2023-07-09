from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True, slots=True)
class DellDevice:
    device_type: str
    name: str
    service_tag: str
    warranty_type: Optional[str]
    warranty_expiration_date: Optional[datetime]

    def __hash__(self) -> int:
        return hash(self.service_tag)

    def __eq__(self, other) -> bool:
        if not isinstance(other, DellDevice):
            return False

        return self.service_tag == other.service_tag

    def __str__(self) -> str:
        if self.has_warranty():
            remaining_days = abs(self.get_days_until_warranty_expires())
            warranty_date_text = self.warranty_expiration_date.strftime('%d %b %Y')

            if self.has_warranty_expired():
                warranty_text = f'warranty expired {remaining_days} days ago' \
                                f' - {warranty_date_text}'
            else:
                warranty_text = f'under warranty for {remaining_days} more days' \
                                f' - {warranty_date_text}'
        else:
            warranty_text = 'no warranty information'

        if self.device_type == 'other':
            device_type_text = ''
        else:
            device_type_text = f'{self.device_type.capitalize()} '

        return f'{device_type_text}{self.name} [{self.service_tag}] ({warranty_text})'

    def has_warranty(self) -> bool:
        return self.warranty_type is not None

    def has_warranty_expired(self) -> bool:
        if self.has_warranty():
            return self.warranty_expiration_date < datetime.now()

        return True

    def get_days_until_warranty_expires(self) -> int:
        if self.has_warranty():
            return (self.warranty_expiration_date - datetime.now()).days

        return 0
