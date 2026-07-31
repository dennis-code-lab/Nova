import time

start_time = None


def start_stopwatch():
    global start_time
    start_time = time.time()
    return "Stopwatch started."


def stopwatch_time():
    global start_time
    if start_time is None:
        return "Stopwatch is not running."

    elapsed = int(time.time() - start_time)
    return f"Elapsed time: {elapsed} seconds."


def stop_stopwatch():
    global start_time
    if start_time is None:
        return "Stopwatch is not running."

    elapsed = int(time.time() - start_time)
    start_time = None  # Reset the state variable
    return f"Stopwatch stopped at {elapsed} seconds."