from pathlib import Path

from django.conf import settings
from django.test.runner import DiscoverRunner


class MaxKBDiscoverRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_db_engines: dict[str, str | None] = {}

    @staticmethod
    def _default_test_labels() -> list[str]:
        apps_dir = Path(settings.APPS_DIR)
        labels = {
            path.relative_to(apps_dir).with_suffix("").as_posix().replace("/", ".")
            for pattern in ("**/tests.py", "**/test_*.py")
            for path in apps_dir.glob(pattern)
        }
        return sorted(labels)

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        labels = list(test_labels or [])
        if not labels:
            labels = self._default_test_labels()
        if extra_tests is not None:
            kwargs["extra_tests"] = extra_tests
        return super().build_suite(labels, **kwargs)

    def setup_databases(self, **kwargs):
        for alias, database_config in settings.DATABASES.items():
            self._original_db_engines[alias] = database_config.get('ENGINE')
            if database_config.get('ENGINE') == 'dj_db_conn_pool.backends.postgresql':
                database_config['ENGINE'] = 'django.db.backends.postgresql'
        return super().setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        try:
            return super().teardown_databases(old_config, **kwargs)
        finally:
            for alias, engine in self._original_db_engines.items():
                if engine is not None:
                    settings.DATABASES[alias]['ENGINE'] = engine
