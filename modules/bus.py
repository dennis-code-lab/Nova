from modules.logger import log_info, log_error

_listeners = {}
_shared_state = {}

def subscribe(event_type, callback):
    """Allows a dynamic skill plugin to listen for specific global system events."""
    if event_type not in _listeners:
        _listeners[event_type] = []
    _listeners[event_type].append(callback)
    log_info("EventBus", f"Bound subscriber function to event topic: [{event_type}]")

def publish(event_type, data=None):
    """Fires an event across the bus, triggering all subscribed skill handlers."""
    log_info("EventBus", f"Publishing event [{event_type}] with payload: {data}")
    if event_type not in _listeners:
        return

    for callback in _listeners[event_type]:
        try:
            callback(data)
        except Exception as e:
            log_error("EventBus", f"Subscriber crashed while handling [{event_type}]: {e}")

def write_state(key, value):
    """Allows skills to publish global data states for other skills to read."""
    _shared_state[key] = value

def read_state(key, default=None):
    """Allows any skill to safely inspect globally broadcast state metrics."""
    return _shared_state.get(key, default)