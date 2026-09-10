import unittest
from unittest.mock import patch
import modules.bus as bus


class TestSubscribe(unittest.TestCase):

    def setUp(self):
        bus._listeners.clear()

    def tearDown(self):
        bus._listeners.clear()

    @patch("modules.bus.log_info")
    def test_subscribe_creates_new_event_topic(self, mock_log_info):
        callback = lambda data: data

        bus.subscribe("test_event", callback)

        self.assertIn("test_event", bus._listeners)
        self.assertEqual(bus._listeners["test_event"], [callback])

    @patch("modules.bus.log_info")
    def test_subscribe_adds_callback_to_existing_topic(
        self,
        mock_log_info,
    ):
        first_callback = lambda data: data
        second_callback = lambda data: data

        bus.subscribe("test_event", first_callback)
        bus.subscribe("test_event", second_callback)

        self.assertEqual(
            bus._listeners["test_event"],
            [first_callback, second_callback],
        )

    @patch("modules.bus.log_info")
    def test_subscribe_allows_duplicate_callback(
        self,
        mock_log_info,
    ):
        callback = lambda data: data

        bus.subscribe("test_event", callback)
        bus.subscribe("test_event", callback)

        self.assertEqual(
            bus._listeners["test_event"],
            [callback, callback],
        )

    @patch("modules.bus.log_info")
    def test_subscribe_logs_binding_message(
        self,
        mock_log_info,
    ):
        callback = lambda data: data

        bus.subscribe("test_event", callback)

        mock_log_info.assert_called_once_with(
            "EventBus",
            "Bound subscriber function to event topic: [test_event]",
        )

    @patch("modules.bus.log_info")
    def test_subscribe_preserves_registration_order(
        self,
        mock_log_info,
    ):
        callbacks = [
            lambda data: data,
            lambda data: data,
            lambda data: data,
        ]

        for callback in callbacks:
            bus.subscribe("test_event", callback)

        self.assertEqual(
            bus._listeners["test_event"],
            callbacks,
        )


class TestPublish(unittest.TestCase):

    def setUp(self):
        bus._listeners.clear()

    def tearDown(self):
        bus._listeners.clear()

    @patch("modules.bus.log_info")
    def test_publish_with_no_subscribers_returns_none(
        self,
        mock_log_info,
    ):
        result = bus.publish("test_event", {"value": 1})

        self.assertIsNone(result)

    @patch("modules.bus.log_info")
    def test_publish_with_no_subscribers_still_logs_event(
        self,
        mock_log_info,
    ):
        bus.publish("test_event", {"value": 1})

        mock_log_info.assert_called_once_with(
            "EventBus",
            "Publishing event [test_event] with payload: {'value': 1}",
        )

    @patch("modules.bus.log_info")
    def test_publish_calls_subscriber_with_data(
        self,
        mock_log_info,
    ):
        callback = unittest.mock.Mock()

        bus._listeners["test_event"] = [callback]

        result = bus.publish("test_event", {"value": 42})

        callback.assert_called_once_with({"value": 42})
        self.assertIsNone(result)

    @patch("modules.bus.log_info")
    def test_publish_calls_all_subscribers(
        self,
        mock_log_info,
    ):
        first_callback = unittest.mock.Mock()
        second_callback = unittest.mock.Mock()
        third_callback = unittest.mock.Mock()

        bus._listeners["test_event"] = [
            first_callback,
            second_callback,
            third_callback,
        ]

        bus.publish("test_event", "payload")

        first_callback.assert_called_once_with("payload")
        second_callback.assert_called_once_with("payload")
        third_callback.assert_called_once_with("payload")

    @patch("modules.bus.log_info")
    def test_publish_preserves_subscriber_execution_order(
        self,
        mock_log_info,
    ):
        calls = []

        def first_callback(data):
            calls.append(("first", data))

        def second_callback(data):
            calls.append(("second", data))

        def third_callback(data):
            calls.append(("third", data))

        bus._listeners["test_event"] = [
            first_callback,
            second_callback,
            third_callback,
        ]

        bus.publish("test_event", "payload")

        self.assertEqual(
            calls,
            [
                ("first", "payload"),
                ("second", "payload"),
                ("third", "payload"),
            ],
        )

    @patch("modules.bus.log_error")
    @patch("modules.bus.log_info")
    def test_publish_continues_after_subscriber_failure(
        self,
        mock_log_info,
        mock_log_error,
    ):
        successful_callback = unittest.mock.Mock()

        def failing_callback(data):
            raise RuntimeError("subscriber failure")

        bus._listeners["test_event"] = [
            failing_callback,
            successful_callback,
        ]

        bus.publish("test_event", "payload")

        successful_callback.assert_called_once_with("payload")

    @patch("modules.bus.log_error")
    @patch("modules.bus.log_info")
    def test_publish_logs_subscriber_exception(
        self,
        mock_log_info,
        mock_log_error,
    ):
        def failing_callback(data):
            raise RuntimeError("subscriber failure")

        bus._listeners["test_event"] = [failing_callback]

        bus.publish("test_event", "payload")

        mock_log_error.assert_called_once_with(
            "EventBus",
            "Subscriber crashed while handling "
            "[test_event]: subscriber failure",
        )

    @patch("modules.bus.log_info")
    def test_publish_passes_none_when_data_omitted(
        self,
        mock_log_info,
    ):
        callback = unittest.mock.Mock()
        bus._listeners["test_event"] = [callback]

        bus.publish("test_event")

        callback.assert_called_once_with(None)

    @patch("modules.bus.log_info")
    def test_publish_can_publish_none_explicitly(
        self,
        mock_log_info,
    ):
        callback = unittest.mock.Mock()
        bus._listeners["test_event"] = [callback]

        bus.publish("test_event", None)

        callback.assert_called_once_with(None)

    @patch("modules.bus.log_info")
    def test_publish_only_notifies_matching_event_topic(
        self,
        mock_log_info,
    ):
        matching_callback = unittest.mock.Mock()
        other_callback = unittest.mock.Mock()

        bus._listeners["matching_event"] = [matching_callback]
        bus._listeners["other_event"] = [other_callback]

        bus.publish("matching_event", "data")

        matching_callback.assert_called_once_with("data")
        other_callback.assert_not_called()


class TestSharedState(unittest.TestCase):

    def setUp(self):
        bus._shared_state.clear()

    def tearDown(self):
        bus._shared_state.clear()

    def test_write_state_stores_value(self):
        bus.write_state("status", "active")

        self.assertEqual(
            bus._shared_state["status"],
            "active",
        )

    def test_read_state_returns_stored_value(self):
        bus.write_state("status", "active")

        result = bus.read_state("status")

        self.assertEqual(result, "active")

    def test_read_state_returns_default_for_missing_key(self):
        result = bus.read_state("missing", "fallback")

        self.assertEqual(result, "fallback")

    def test_read_state_returns_none_by_default_for_missing_key(self):
        result = bus.read_state("missing")

        self.assertIsNone(result)

    def test_write_state_overwrites_existing_value(self):
        bus.write_state("status", "inactive")
        bus.write_state("status", "active")

        self.assertEqual(
            bus.read_state("status"),
            "active",
        )

    def test_write_state_supports_none_as_value(self):
        bus.write_state("status", None)

        self.assertIn("status", bus._shared_state)
        self.assertIsNone(bus.read_state("status"))

    def test_read_state_distinguishes_stored_none_from_missing_default(self):
        bus.write_state("status", None)

        self.assertIsNone(
            bus.read_state("status", "fallback"),
        )

    def test_shared_state_supports_different_value_types(self):
        values = {
            "string": "Nova",
            "number": 42,
            "boolean": True,
            "list": ["a", "b"],
            "dictionary": {"key": "value"},
        }

        for key, value in values.items():
            with self.subTest(key=key):
                bus.write_state(key, value)
                self.assertEqual(
                    bus.read_state(key),
                    value,
                )


class TestSubscribeAndPublishIntegration(unittest.TestCase):

    def setUp(self):
        bus._listeners.clear()

    def tearDown(self):
        bus._listeners.clear()

    @patch("modules.bus.log_info")
    def test_subscribe_then_publish_delivers_event(
        self,
        mock_log_info,
    ):
        received = []

        def callback(data):
            received.append(data)

        bus.subscribe("status_changed", callback)
        bus.publish("status_changed", {"status": "ready"})

        self.assertEqual(
            received,
            [{"status": "ready"}],
        )

    @patch("modules.bus.log_info")
    def test_multiple_subscribers_receive_same_payload(
        self,
        mock_log_info,
    ):
        received_first = []
        received_second = []

        def first_callback(data):
            received_first.append(data)

        def second_callback(data):
            received_second.append(data)

        bus.subscribe("event", first_callback)
        bus.subscribe("event", second_callback)

        payload = {"message": "hello"}
        bus.publish("event", payload)

        self.assertEqual(received_first, [payload])
        self.assertEqual(received_second, [payload])


if __name__ == "__main__":
    unittest.main()