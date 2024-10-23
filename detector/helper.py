def sl_error_to_exception(error: SLError):
    if error != 0:
        raise RuntimeError("Got SLError")