import socket
import shutil
import getpass

try:
    import psutil
except ImportError:
    psutil = None


def get_computer_name():

    return socket.gethostname()


def get_current_user():

    return getpass.getuser()


def get_ip_address():

    try:

        s = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        s.connect(
            ("8.8.8.8", 80)
        )

        ip = s.getsockname()[0]

        s.close()

        return ip

    except Exception as e:

        return (
            f"Unable to get IP address: {e}"
        )


def get_disk_space():

    try:

        total, used, free = shutil.disk_usage(
            "C:\\"
        )

        return (
            f"Total: {total // (2**30)} GB, "
            f"Used: {used // (2**30)} GB, "
            f"Free: {free // (2**30)} GB"
        )

    except Exception as e:

        return (
            f"Disk space error: {e}"
        )


def get_battery_status():

    if psutil is None:

        return (
            "Battery information unavailable. "
            "Install psutil with: pip install psutil"
        )

    try:

        battery = psutil.sensors_battery()

        if battery is None:

            return "No battery detected."

        plugged = (
            "Charging"
            if battery.power_plugged
            else "Not charging"
        )

        return (
            f"{battery.percent}% - {plugged}"
        )

    except Exception as e:

        return (
            f"Battery error: {e}"
        )