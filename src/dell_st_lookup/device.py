from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class DellDevice:
    device_type: str
    name: str
    service_tag: str
    warranty_type: str
    warranty_expiration_date: datetime

    def __hash__(self) -> int:
        return hash(self.service_tag)

    def __eq__(self, other) -> bool:
        if not isinstance(other, DellDevice):
            return False

        return self.service_tag == other.service_tag

    def __str__(self) -> str:
        remaining_days = abs(self.get_days_until_warranty_expires())
        warranty_date_text = self.warranty_expiration_date.strftime('%d %b %Y')

        if self.has_warranty_expired():
            warranty_text = f'warranty expired {remaining_days} days ago - {warranty_date_text}'
        else:
            warranty_text = f'under warranty for {remaining_days} more days - {warranty_date_text}'

        return f'{self.device_type.capitalize()} {self.name} [{self.service_tag}] ({warranty_text})'

    def has_warranty_expired(self) -> bool:
        return self.warranty_expiration_date < datetime.now()

    def get_days_until_warranty_expires(self) -> int:
        return (self.warranty_expiration_date - datetime.now()).days
