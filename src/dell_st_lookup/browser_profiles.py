from typing import NamedTuple, Type

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.safari.webdriver import WebDriver as SafariDriver
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.safari.service import Service as SafariService

WebDriverType = Type[ChromeDriver] | Type[EdgeDriver] | Type[FirefoxDriver] | Type[SafariDriver]
OptionsType = Type[ChromeOptions] | Type[EdgeOptions] | Type[FirefoxOptions] | Type[SafariOptions]
ServiceType = Type[ChromeService] | Type[EdgeService] | Type[FirefoxService] | Type[SafariService]


class BrowserProfile(NamedTuple):
    init: WebDriverType
    options: OptionsType
    service: ServiceType


CHROME_PROFILE = BrowserProfile(
    init=ChromeDriver,
    options=ChromeOptions,
    service=ChromeService
)

EDGE_PROFILE = BrowserProfile(
    init=EdgeDriver,
    options=EdgeOptions,
    service=EdgeService
)

FIREFOX_PROFILE = BrowserProfile(
    init=FirefoxDriver,
    options=FirefoxOptions,
    service=FirefoxService
)

SAFARI_PROFILE = BrowserProfile(
    init=SafariDriver,
    options=SafariOptions,
    service=SafariService
)
