import os
import traceback

def handleNotImplementedError(error: str):
    if os.getenv("AUTOSAR_IGNORE_NOT_IMPLEMENTED_ERROR") == "1":
        try: 
            raise NotImplementedError(error)
        except NotImplementedError as e:
            print(f"WARNING - ignoring NotImplementedError '{e}' in:")
            print(traceback.format_exc())
    else:
        raise NotImplementedError(error)