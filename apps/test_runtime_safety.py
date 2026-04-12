from importlib import import_module
from types import SimpleNamespace
from unittest.mock import PropertyMock, patch

import psutil
from django.conf import settings
from django.test import SimpleTestCase

import main

BaseService = import_module('common.management.commands.services.services.base').BaseService
Services = import_module('common.management.commands.services.command').Services
GunicornLocalModelService = import_module(
    'common.management.commands.services.services.local_model'
).GunicornLocalModelService
Config = import_module('maxkb.conf').Config


class ConfigAllowedHostsTests(SimpleTestCase):
    def test_get_allowed_hosts_uses_safe_local_defaults(self):
        config = Config()
        config['DEBUG'] = True

        self.assertEqual(
            config.get_allowed_hosts(),
            ['127.0.0.1', 'localhost', '[::1]', 'testserver'],
        )

    def test_get_allowed_hosts_requires_explicit_value_when_debug_disabled(self):
        config = Config()
        config['DEBUG'] = False

        with self.assertRaises(ImportError) as context:
            config.get_allowed_hosts()

        self.assertEqual(str(context.exception), 'Missing required configuration: MAXKB_ALLOWED_HOSTS')

    def test_get_allowed_hosts_parses_comma_separated_value(self):
        config = Config()
        config['ALLOWED_HOSTS'] = 'example.com, api.example.com ,localhost'

        self.assertEqual(
            config.get_allowed_hosts(),
            ['example.com', 'api.example.com', 'localhost'],
        )

    def test_enable_local_model_defaults_to_explicit_opt_in(self):
        config = Config()

        self.assertFalse(config.get_enable_local_model())

    def test_enable_local_model_reads_truthy_values(self):
        config = Config()
        config['ENABLE_LOCAL_MODEL'] = 'true'

        self.assertTrue(config.get_enable_local_model())


class MainRuntimeSafetyTests(SimpleTestCase):
    @patch('main.sys.exit')
    @patch('main.logging.error')
    @patch('main.management.call_command', side_effect=RuntimeError('boom'))
    def test_collect_static_exits_when_collection_fails(self, call_command, log_error, sys_exit):
        main.collect_static()

        call_command.assert_called_once_with('collectstatic', '--no-input', '-c', verbosity=0, interactive=False)
        log_error.assert_called_once()
        sys_exit.assert_called_once_with(10)

    @patch('main.time.sleep')
    @patch('main.sys.exit')
    @patch('main.logging.error')
    @patch('main.management.call_command', side_effect=RuntimeError('start failed'))
    def test_start_services_exits_when_service_start_fails(self, call_command, log_error, sys_exit, sleep):
        main.args = SimpleNamespace(services=['web'], daemon=False, force=False, worker=None)
        main.action = 'start'

        main.start_services()

        call_command.assert_called_once_with('start', 'web')
        log_error.assert_called_once()
        sleep.assert_called_once_with(2)
        sys_exit.assert_called_once_with(12)

    @patch('main.sys.exit')
    @patch('main.logging.error')
    @patch('main.management.call_command', side_effect=RuntimeError('migrate failed'))
    def test_perform_db_migrate_exits_when_migration_fails(self, call_command, log_error, sys_exit):
        main.perform_db_migrate()

        call_command.assert_called_once_with('migrate')
        log_error.assert_called_once()
        sys_exit.assert_called_once_with(11)

    def test_configure_local_model_runtime_env_sets_model_specific_paths(self):
        with patch.dict('main.os.environ', {}, clear=False):
            main.configure_local_model_runtime_env()

            self.assertEqual(main.os.environ['HF_HOME'], '/opt/maxkb-app/model/base')
            self.assertEqual(main.os.environ['TMPDIR'], '/opt/maxkb-app/tmp')

    @patch('main.configure_local_model_runtime_env')
    @patch('main.management.call_command')
    def test_dev_local_model_runs_with_local_model_bind(self, call_command, configure_env):
        main.args = SimpleNamespace(services=['local_model'])

        config = Config()
        config['LOCAL_MODEL_HOST'] = '127.0.0.1'
        config['LOCAL_MODEL_PORT'] = '11636'

        with patch.dict('sys.modules', {'maxkb.const': SimpleNamespace(CONFIG=config)}):
            main.dev()

        configure_env.assert_called_once_with()
        call_command.assert_called_once_with('runserver', '127.0.0.1:11636')


class RuntimeProfileAllowedHostsTests(SimpleTestCase):
    def test_active_settings_use_explicit_allowed_hosts_contract(self):
        self.assertEqual(settings.ALLOWED_HOSTS[:3], ['127.0.0.1', 'localhost', 'testserver'])


class DummyService(BaseService):
    @property
    def cmd(self):
        return ['python']

    @property
    def cwd(self):
        return ''


class ServiceBaseRuntimeSafetyTests(SimpleTestCase):
    @patch('common.management.commands.services.services.base.logging.warning')
    @patch('common.management.commands.services.services.base.psutil.Process', side_effect=psutil.Error('missing'))
    def test_process_lookup_logs_warning_instead_of_swallowing(self, process_cls, log_warning):
        service = DummyService(name='dummy')
        with patch.object(DummyService, 'pid', new_callable=PropertyMock, return_value=1234):
            self.assertIsNone(service.process)

        process_cls.assert_called_once_with(1234)
        log_warning.assert_called_once()


class LocalModelRuntimeIsolationTests(SimpleTestCase):
    def test_web_services_excludes_local_model_by_default(self):
        with patch('common.management.commands.services.command.CONFIG.get_enable_local_model', return_value=False):
            self.assertEqual(Services.web_services(), [Services.gunicorn])

    def test_web_services_includes_local_model_when_enabled(self):
        with patch('common.management.commands.services.command.CONFIG.get_enable_local_model', return_value=True):
            self.assertEqual(Services.web_services(), [Services.gunicorn, Services.local_model])

    @patch('common.management.commands.services.services.local_model.subprocess.Popen')
    @patch('common.management.commands.services.services.local_model.os.environ', {'BASE': '1'})
    def test_local_model_subprocess_sets_runtime_env(self, popen_mock):
        service = GunicornLocalModelService(name='local_model', worker_gunicorn=1)

        with patch.object(GunicornLocalModelService, 'log_file', new_callable=PropertyMock, return_value=None):
            service.open_subprocess()

        popen_kwargs = popen_mock.call_args.kwargs
        self.assertEqual(popen_kwargs['env']['SERVER_NAME'], 'local_model')
        self.assertEqual(popen_kwargs['env']['HF_HOME'], '/opt/maxkb-app/model/base')
        self.assertEqual(popen_kwargs['env']['TMPDIR'], '/opt/maxkb-app/tmp')
