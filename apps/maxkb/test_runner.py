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

    @staticmethod
    def _resolve_label_path(label: str) -> Path | None:
        apps_dir = Path(settings.APPS_DIR)
        parts = [part for part in label.split('.') if part]
        candidates = [parts]
        if parts[:1] == ['apps']:
            candidates.append(parts[1:])

        for candidate in candidates:
            if not candidate:
                continue
            candidate_path = apps_dir.joinpath(*candidate)
            if candidate_path.is_dir():
                return candidate_path

        return None

    @classmethod
    def _expand_test_labels(cls, test_labels: list[str]) -> list[str]:
        apps_dir = Path(settings.APPS_DIR)
        expanded_labels = []
        seen = set()

        for label in test_labels:
            label_path = cls._resolve_label_path(label)
            if label_path is None:
                candidate_labels = [label]
            else:
                candidate_labels = sorted({
                    path.relative_to(apps_dir).with_suffix('').as_posix().replace('/', '.')
                    for pattern in ('**/tests.py', '**/test_*.py')
                    for path in label_path.glob(pattern)
                }) or [label]

            for candidate_label in candidate_labels:
                if candidate_label not in seen:
                    seen.add(candidate_label)
                    expanded_labels.append(candidate_label)

        return expanded_labels

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        labels = list(test_labels or [])
        if not labels:
            labels = self._default_test_labels()
        else:
            labels = self._expand_test_labels(labels)
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
