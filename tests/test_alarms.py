"""
Nova Engine v138
Alarms Module Tests
Verifies alarm loading, saving, creation, listing, deletion,
duplicate handling, missing-file behavior, invalid JSON
fallbacks, and current-time alarm checks.
"""
import json
import unittest
from unittest.mock import mock_open, patch
import modules.alarms as alarms


class TestLoadAlarms(unittest.TestCase):

    def test_missing_alarm_file_returns_empty_list(self):
        with patch(
            "modules.alarms.os.path.exists",
            return_value=False,
        ):
            result = alarms.load_alarms()

        self.assertEqual(result, [])

    def test_valid_alarm_file_returns_decoded_data(self):
        alarm_data = ["08:00", "14:30", "21:45"]

        with patch(
            "modules.alarms.os.path.exists",
            return_value=True,
        ), patch(
            "builtins.open",
            mock_open(
                read_data=json.dumps(alarm_data),
            ),
        ):
            result = alarms.load_alarms()

        self.assertEqual(result, alarm_data)

    def test_empty_alarm_file_returns_empty_list_on_json_error(
        self,
    ):
        with patch(
            "modules.alarms.os.path.exists",
            return_value=True,
        ), patch(
            "builtins.open",
            mock_open(
                read_data="",
            ),
        ):
            result = alarms.load_alarms()

        self.assertEqual(result, [])

    def test_invalid_json_returns_empty_list(self):
        with patch(
            "modules.alarms.os.path.exists",
            return_value=True,
        ), patch(
            "builtins.open",
            mock_open(
                read_data="{invalid json",
            ),
        ):
            result = alarms.load_alarms()

        self.assertEqual(result, [])

    def test_file_read_exception_returns_empty_list(self):
        with patch(
            "modules.alarms.os.path.exists",
            return_value=True,
        ), patch(
            "builtins.open",
            side_effect=OSError("read failure"),
        ):
            result = alarms.load_alarms()

        self.assertEqual(result, [])


class TestSaveAlarms(unittest.TestCase):

    def test_save_alarms_creates_data_directory(self):
        alarm_data = ["08:00"]

        with patch(
            "modules.alarms.os.makedirs",
        ) as makedirs, patch(
            "builtins.open",
            mock_open(),
        ):
            alarms.save_alarms(alarm_data)

        makedirs.assert_called_once_with(
            "data",
            exist_ok=True,
        )

    def test_save_alarms_opens_expected_file_for_writing(self):
        alarm_data = ["08:00", "18:30"]

        with patch(
            "modules.alarms.os.makedirs",
        ), patch(
            "builtins.open",
            mock_open(),
        ) as open_file:
            alarms.save_alarms(alarm_data)

        open_file.assert_called_once_with(
            alarms.ALARMS_FILE,
            "w",
            encoding="utf-8",
        )

    def test_save_alarms_writes_json_with_indentation(self):
        alarm_data = ["08:00", "18:30"]

        mocked_file = mock_open()

        with patch(
            "modules.alarms.os.makedirs",
        ), patch(
            "builtins.open",
            mocked_file,
        ):
            alarms.save_alarms(alarm_data)

        handle = mocked_file.return_value

        written = "".join(
            call.args[0]
            for call in handle.write.call_args_list
        )
        self.assertEqual(
            written,
            json.dumps(
                alarm_data,
                indent=4,
            ),
        )

    def test_save_alarms_preserves_alarm_data(self):
        alarm_data = [
            "06:30",
            "12:00",
            "22:15",
        ]

        mocked_file = mock_open()

        with patch(
            "modules.alarms.os.makedirs",
        ), patch(
            "builtins.open",
            mocked_file,
        ):
            alarms.save_alarms(alarm_data)

        written = "".join(
            call.args[0]
            for call in mocked_file.return_value.write.call_args_list
        )

        self.assertEqual(
            json.loads(written),
            alarm_data,
        )


class TestAddAlarm(unittest.TestCase):

    def test_add_alarm_appends_new_alarm(self):
        existing = ["08:00"]

        with patch(
            "modules.alarms.load_alarms",
            return_value=existing,
        ), patch(
            "modules.alarms.save_alarms",
        ) as save:
            result = alarms.add_alarm("14:30")

        self.assertEqual(
            result,
            "Alarm set for 14:30",
        )
        self.assertEqual(
            existing,
            ["08:00", "14:30"],
        )
        save.assert_called_once_with(
            ["08:00", "14:30"],
        )

    def test_add_alarm_to_empty_list_creates_first_alarm(self):
        existing = []

        with patch(
            "modules.alarms.load_alarms",
            return_value=existing,
        ), patch(
            "modules.alarms.save_alarms",
        ) as save:
            result = alarms.add_alarm("09:15")

        self.assertEqual(
            result,
            "Alarm set for 09:15",
        )
        self.assertEqual(
            existing,
            ["09:15"],
        )
        save.assert_called_once_with(["09:15"])

    def test_duplicate_alarm_is_rejected(self):
        existing = ["08:00", "14:30"]

        with patch(
            "modules.alarms.load_alarms",
            return_value=existing,
        ), patch(
            "modules.alarms.save_alarms",
        ) as save:
            result = alarms.add_alarm("14:30")

        self.assertEqual(
            result,
            "Alarm already exists.",
        )
        self.assertEqual(
            existing,
            ["08:00", "14:30"],
        )
        save.assert_not_called()

    def test_duplicate_check_is_based_on_exact_value(self):
        existing = ["08:00"]

        with patch(
            "modules.alarms.load_alarms",
            return_value=existing,
        ), patch(
            "modules.alarms.save_alarms",
        ) as save:
            result = alarms.add_alarm("8:00")

        self.assertEqual(
            result,
            "Alarm set for 8:00",
        )
        save.assert_called_once_with(
            ["08:00", "8:00"],
        )


class TestListAlarms(unittest.TestCase):

    def test_empty_alarm_list_returns_no_alarms_message(self):
        with patch(
            "modules.alarms.load_alarms",
            return_value=[],
        ):
            result = alarms.list_alarms()

        self.assertEqual(
            result,
            "No alarms set.",
        )

    def test_populated_alarm_list_is_formatted_on_separate_lines(
        self,
    ):
        with patch(
            "modules.alarms.load_alarms",
            return_value=[
                "08:00",
                "14:30",
                "21:45",
            ],
        ):
            result = alarms.list_alarms()

        self.assertEqual(
            result,
            "Alarms:\n08:00\n14:30\n21:45",
        )

    def test_single_alarm_is_formatted_correctly(self):
        with patch(
            "modules.alarms.load_alarms",
            return_value=["07:30"],
        ):
            result = alarms.list_alarms()

        self.assertEqual(
            result,
            "Alarms:\n07:30",
        )

    def test_list_alarms_preserves_alarm_order(self):
        alarm_data = [
            "22:00",
            "06:30",
            "13:15",
        ]

        with patch(
            "modules.alarms.load_alarms",
            return_value=alarm_data,
        ):
            result = alarms.list_alarms()

        self.assertEqual(
            result.splitlines(),
            [
                "Alarms:",
                "22:00",
                "06:30",
                "13:15",
            ],
        )


class TestDeleteAlarm(unittest.TestCase):

    def test_delete_existing_alarm_removes_alarm(self):
        existing = [
            "08:00",
            "14:30",
            "21:45",
        ]

        with patch(
            "modules.alarms.load_alarms",
            return_value=existing,
        ), patch(
            "modules.alarms.save_alarms",
        ) as save:
            result = alarms.delete_alarm("14:30")

        self.assertEqual(
            result,
            "Alarm 14:30 deleted.",
        )
        self.assertEqual(
            existing,
            ["08:00", "21:45"],
        )
        save.assert_called_once_with(
            ["08:00", "21:45"],
        )

    def test_delete_missing_alarm_returns_not_found(self):
        existing = ["08:00", "21:45"]

        with patch(
            "modules.alarms.load_alarms",
            return_value=existing,
        ), patch(
            "modules.alarms.save_alarms",
        ) as save:
            result = alarms.delete_alarm("14:30")

        self.assertEqual(
            result,
            "Alarm not found.",
        )
        self.assertEqual(
            existing,
            ["08:00", "21:45"],
        )
        save.assert_not_called()

    def test_delete_from_empty_alarm_list_returns_not_found(
        self,
    ):
        with patch(
            "modules.alarms.load_alarms",
            return_value=[],
        ), patch(
            "modules.alarms.save_alarms",
        ) as save:
            result = alarms.delete_alarm("08:00")

        self.assertEqual(
            result,
            "Alarm not found.",
        )
        save.assert_not_called()

    def test_delete_alarm_removes_only_one_matching_occurrence(
        self,
    ):
        existing = [
            "08:00",
            "14:30",
            "14:30",
            "21:45",
        ]

        with patch(
            "modules.alarms.load_alarms",
            return_value=existing,
        ), patch(
            "modules.alarms.save_alarms",
        ) as save:
            result = alarms.delete_alarm("14:30")

        self.assertEqual(
            result,
            "Alarm 14:30 deleted.",
        )
        self.assertEqual(
            existing,
            [
                "08:00",
                "14:30",
                "21:45",
            ],
        )
        save.assert_called_once_with(
            [
                "08:00",
                "14:30",
                "21:45",
            ],
        )


class TestCheckAlarms(unittest.TestCase):

    def test_matching_current_time_returns_alarm_message(self):
        with patch(
            "modules.alarms.datetime",
        ) as datetime_mock:
            datetime_mock.now.return_value.strftime.return_value = (
                "14:30"
            )

            with patch(
                "modules.alarms.load_alarms",
                return_value=["08:00", "14:30"],
            ):
                result = alarms.check_alarms()

        self.assertEqual(
            result,
            "ALARM! It is now 14:30.",
        )

    def test_non_matching_current_time_returns_none(self):
        with patch(
            "modules.alarms.datetime",
        ) as datetime_mock:
            datetime_mock.now.return_value.strftime.return_value = (
                "14:30"
            )

            with patch(
                "modules.alarms.load_alarms",
                return_value=["08:00", "21:45"],
            ):
                result = alarms.check_alarms()

        self.assertIsNone(result)

    def test_empty_alarm_list_returns_none(self):
        with patch(
            "modules.alarms.datetime",
        ) as datetime_mock:
            datetime_mock.now.return_value.strftime.return_value = (
                "14:30"
            )

            with patch(
                "modules.alarms.load_alarms",
                return_value=[],
            ):
                result = alarms.check_alarms()

        self.assertIsNone(result)

    def test_check_alarms_uses_hour_minute_format(self):
        with patch(
            "modules.alarms.datetime",
        ) as datetime_mock:
            datetime_mock.now.return_value.strftime.assert_not_called()

            datetime_mock.now.return_value.strftime.return_value = (
                "09:05"
            )

            with patch(
                "modules.alarms.load_alarms",
                return_value=["09:05"],
            ):
                result = alarms.check_alarms()

        datetime_mock.now.return_value.strftime.assert_called_once_with(
            "%H:%M",
        )

        self.assertEqual(
            result,
            "ALARM! It is now 09:05.",
        )


if __name__ == "__main__":
    unittest.main()