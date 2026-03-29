from django.test import TestCase
from rest_framework import serializers

from trigger.models import TriggerTypeChoices, TriggerTaskTypeChoices
from trigger.serializers.trigger import TriggerValidationMixin


class ConcreteValidator(TriggerValidationMixin, serializers.Serializer):
    trigger_type = serializers.ChoiceField(choices=TriggerTypeChoices.choices)
    trigger_setting = serializers.DictField()


class TimeFormatValidationTests(TestCase):
    def test_valid_time(self):
        validator = ConcreteValidator()
        validator._validate_time_format("09:00")

    def test_valid_midnight(self):
        validator = ConcreteValidator()
        validator._validate_time_format("00:00")

    def test_valid_end_of_day(self):
        validator = ConcreteValidator()
        validator._validate_time_format("23:59")

    def test_invalid_format_letter(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_time_format("ab:cd")

    def test_invalid_hour_24(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_time_format("24:00")

    def test_invalid_minute_60(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_time_format("12:60")

    def test_missing_colon(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_time_format("0900")


class NonEmptyArrayValidationTests(TestCase):
    def test_valid_array(self):
        validator = ConcreteValidator()
        validator._validate_non_empty_array([1, 2, 3], "test")

    def test_empty_array_rejected(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_non_empty_array([], "test")

    def test_non_array_rejected(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_non_empty_array("not array", "test")


class NumberRangeValidationTests(TestCase):
    def test_valid_range(self):
        validator = ConcreteValidator()
        validator._validate_number_range([1, 3, 5, 7], "days", 1, 7)

    def test_out_of_range_rejected(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_number_range([1, 8], "days", 1, 7)

    def test_non_numeric_rejected(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_number_range(["abc"], "days", 1, 7)


class ScheduledSettingValidationTests(TestCase):
    def test_valid_daily(self):
        validator = ConcreteValidator()
        validator._validate_scheduled_setting({
            "schedule_type": "daily",
            "time": ["09:00", "18:00"]
        })

    def test_valid_weekly(self):
        validator = ConcreteValidator()
        validator._validate_scheduled_setting({
            "schedule_type": "weekly",
            "days": [1, 3, 5],
            "time": ["09:00"]
        })

    def test_valid_monthly(self):
        validator = ConcreteValidator()
        validator._validate_scheduled_setting({
            "schedule_type": "monthly",
            "days": [1, 15],
            "time": ["08:00"]
        })

    def test_valid_interval(self):
        validator = ConcreteValidator()
        validator._validate_scheduled_setting({
            "schedule_type": "interval",
            "interval_value": 5,
            "interval_unit": "minutes"
        })

    def test_valid_cron(self):
        validator = ConcreteValidator()
        validator._validate_scheduled_setting({
            "schedule_type": "cron",
            "cron_expression": "0 9 * * *"
        })

    def test_invalid_schedule_type(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_scheduled_setting({
                "schedule_type": "invalid"
            })

    def test_daily_missing_time(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_scheduled_setting({
                "schedule_type": "daily"
            })

    def test_weekly_missing_days(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_scheduled_setting({
                "schedule_type": "weekly",
                "time": ["09:00"]
            })

    def test_interval_invalid_value(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_scheduled_setting({
                "schedule_type": "interval",
                "interval_value": 0,
                "interval_unit": "minutes"
            })

    def test_interval_invalid_unit(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_scheduled_setting({
                "schedule_type": "interval",
                "interval_value": 5,
                "interval_unit": "seconds"
            })


class EventSettingValidationTests(TestCase):
    def test_valid_event_with_body(self):
        validator = ConcreteValidator()
        validator._validate_event_setting({"body": [{"key": "value"}]})

    def test_valid_event_without_body(self):
        validator = ConcreteValidator()
        validator._validate_event_setting({})

    def test_body_must_be_array(self):
        validator = ConcreteValidator()
        with self.assertRaises(serializers.ValidationError):
            validator._validate_event_setting({"body": "not array"})


class TriggerTypeChoicesTests(TestCase):
    def test_scheduled_type(self):
        self.assertEqual(TriggerTypeChoices.SCHEDULED.value, "SCHEDULED")

    def test_event_type(self):
        self.assertEqual(TriggerTypeChoices.EVENT.value, "EVENT")

    def test_choices_count(self):
        self.assertEqual(len(TriggerTypeChoices.choices), 2)


class TriggerTaskTypeChoicesTests(TestCase):
    def test_application_type(self):
        self.assertEqual(TriggerTaskTypeChoices.APPLICATION.value, "APPLICATION")

    def test_tool_type(self):
        self.assertEqual(TriggerTaskTypeChoices.TOOL.value, "TOOL")
