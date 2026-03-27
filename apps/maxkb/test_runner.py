from pathlib import Path

from django.conf import settings
from django.test.runner import DiscoverRunner


class MaxKBDiscoverRunner(DiscoverRunner):
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
