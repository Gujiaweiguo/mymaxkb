# coding=utf-8

from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.job.scheduler import scheduler
from common.utils.lock import RedisLock, lock
from common.utils.logger import maxkb_logger
from system_manage.models import Log, SettingType, SystemSetting


def clean_operation_log_job():
    clean_operation_log_job_lock()


@lock(lock_key='clean_operation_log_job_execute', timeout=30)
def clean_operation_log_job_lock():
    maxkb_logger.info(_('start clean operation log'))
    clean_time = _get_clean_time()
    cutoff_time = timezone.now() - timedelta(days=clean_time)
    batch_size = 500

    while True:
        with transaction.atomic():
            log_ids = list(
                Log.objects.filter(create_time__lt=cutoff_time)
                .order_by('create_time')
                .values_list('id', flat=True)[:batch_size]
            )
            if not log_ids:
                break
            deleted_count = Log.objects.filter(id__in=log_ids).delete()[0]
            if deleted_count < batch_size:
                break

    maxkb_logger.info(_('end clean operation log'))


def _get_clean_time() -> int:
    system_setting = SystemSetting.objects.filter(type=SettingType.LOG).first()
    if system_setting is None:
        return 180
    return int(system_setting.meta.get('clean_time', 180))


def run():
    rlock = RedisLock()
    if rlock.try_lock('clean_operation_log_job', 30 * 30):
        try:
            maxkb_logger.debug('get lock clean_operation_log_job')

            existing_job = scheduler.get_job(job_id='clean_operation_log')
            if existing_job is not None:
                existing_job.remove()
            scheduler.add_job(
                clean_operation_log_job,
                'cron',
                hour='0',
                minute='10',
                id='clean_operation_log',
            )
        finally:
            rlock.un_lock('clean_operation_log_job')
