import os


def pytest_configure() -> None:
    """Поверх переменных окружения: pytest всегда с `config.settings.test` (InMemory channel layer)."""
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.test"
