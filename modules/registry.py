from modules.logger import log_info, log_error

_services = {}

def register_service(name, service_instance):
    """Registers a core capability or engine as a shared system service."""
    _services[name] = service_instance
    log_info("ServiceRegistry", f"Core service registered successfully: [{name}]")

def get_service(name):
    """Allows any decoupled plugin to request a core system dependency safely."""
    if name not in _services:
        log_error("ServiceRegistry", f"Requested missing dependency service: [{name}]")
        raise RuntimeError(f"Service '{name}' is not registered in Nova's core engine.")
    return _services[name]