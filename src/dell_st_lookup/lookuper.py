from datetime import datetime
from typing import Optional

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from dell_st_lookup.config import Config
from dell_st_lookup.device import DellDevice


class DellServiceTagLookuper:
    _HOMEPAGE = 'https://www.dell.com/support/home/en-uk?lwp=rt'

    def __init__(self, config: Config) -> None:
        options = config.driver_options_function()
        for option in config.driver_options:
            options.add_argument(option)

        service = config.driver_service_function(str(config.driver_executable))

        self.driver = config.driver_init_function(options=options, service=service)  # type: ignore

    def start(self) -> None:
        self.driver.get(self._HOMEPAGE)

        # Accept cookies so it won't get in the way later
        cookie_consent_button: WebElement = WebDriverWait(self.driver, timeout=10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.cc-dismiss'))
        )
        cookie_consent_button.click()

    def get_product(self, service_tag: str) -> Optional[DellDevice]:
        old_html_id = self._get_html_id()

        # Search for the service tag
        search_bar: WebElement = WebDriverWait(self.driver, timeout=10).until(
            EC.presence_of_element_located((By.ID, 'mh-search-input'))
        )
        search_button = self.driver.find_element(By.CSS_SELECTOR, 'button.mh-search-submit')

        search_bar.send_keys(service_tag)
        search_button.click()

        self._wait_for_page_refresh(old_html_id)

        # Wait for warranty info or 404 page to load
        WebDriverWait(self.driver, timeout=30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#hiddenValues, #null-result-text'))
        )

        # Check if it's 404 page
        try:
            if self.driver.find_element(By.ID, 'null-result-text'):
                return None
        except NoSuchElementException:
            pass

        # Get device type
        device_type = self.driver.find_element(
            By.CSS_SELECTOR, 'meta[name=supportproductselected]'
        ).get_attribute('content').split('-')[-1]

        # Get device name
        device_name = self.driver.find_element(
            By.CSS_SELECTOR, 'h1[aria-label=SystemDescription'
        ).text.strip()

        # Get service tag (redundant - I know)
        service_tag = self.driver.find_element(
            By.CLASS_NAME, 'service-tag'
        ).text.strip().split()[-1]

        # Get warranty type
        warranty_type = self.driver.find_element(By.ID, 'WarrantyType').get_attribute('value')

        # Get warranty expiration date
        warranty_expiration_date_text = self.driver.find_element(
            By.CSS_SELECTOR, 'p.warrantyExpiringLabel'
        ).text.strip().split()[-3:]

        warranty_expiration_date = datetime.strptime(
            ' '.join(warranty_expiration_date_text),
            '%d %b %Y'
        )

        return DellDevice(
            device_type=device_type,
            name=device_name,
            service_tag=service_tag,
            warranty_type=warranty_type,
            warranty_expiration_date=warranty_expiration_date
        )

    def _get_html_id(self) -> Optional[str]:
        try:
            return self.driver.find_element(By.TAG_NAME, 'html').id
        except NoSuchElementException:
            return None

    def _wait_for_page_refresh(self, old_html_id: Optional[str]) -> None:
        WebDriverWait(self.driver, timeout=30).until(
            lambda _: self._get_html_id() != old_html_id
        )

    def quit(self) -> None:
        self.driver.quit()
