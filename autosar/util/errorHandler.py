import os
import traceback

already_shown_errors = set()

def handleNotImplementedError(error: str):
    if os.getenv("AUTOSAR_IGNORE_NOT_IMPLEMENTED_ERROR") == "1":
        try: 
            raise NotImplementedError(error)
        except NotImplementedError as e:
            stack_trace = "".join(traceback.format_stack())
            exception = f"WARNING - ignoring NotImplementedError '{e}' in:\n\r{stack_trace}"
            if not exception in already_shown_errors:
                print(exception)
            else:
                already_shown_errors.add(exception)
    else:
        raise NotImplementedError(error)

def handleValueError(error: str):
    if os.getenv("AUTOSAR_IGNORE_NOT_IMPLEMENTED_ERROR") == "1":
        try: 
            raise ValueError(error)
        except ValueError as e:
            stack_trace = "".join(traceback.format_stack())
            exception = f"WARNING - ignoring ValueError '{e}' in:\n\r{stack_trace}"
            if not exception in already_shown_errors:
                print(exception)
            else:
                already_shown_errors.add(exception)
    else:
        raise ValueError(error)