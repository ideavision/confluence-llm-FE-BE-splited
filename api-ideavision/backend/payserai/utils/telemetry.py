import threading
import uuid
from enum import Enum
from typing import cast

import requests

from payserai.configs.app_configs import DISABLE_TELEMETRY
from payserai.dynamic_configs import get_dynamic_config_store
from payserai.dynamic_configs.interface import ConfigNotFoundError

CUSTOMER_UUID_KEY = "customer_uuid"
PAYSERAI_TELEMETRY_ENDPOINT = "https://telemetry.payserai.ai/anonymous_telemetry"


class RecordType(str, Enum):
    VERSION = "version"
    SIGN_UP = "sign_up"
    USAGE = "usage"
    LATENCY = "latency"
    FAILURE = "failure"


def get_or_generate_uuid() -> str:
    kv_store = get_dynamic_config_store()
    try:
        return cast(str, kv_store.load(CUSTOMER_UUID_KEY))
    except ConfigNotFoundError:
        customer_id = str(uuid.uuid4())
        kv_store.store(CUSTOMER_UUID_KEY, customer_id)
        return customer_id


def optional_telemetry(record_type: RecordType, data: dict) -> None:
    if DISABLE_TELEMETRY:
        return

    try:

        def telemetry_logic() -> None:
            try:
                payload = {
                    "data": data,
                    "record": record_type,
                    "customer_uuid": get_or_generate_uuid(),
                }
                requests.post(
                    PAYSERAI_TELEMETRY_ENDPOINT,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                )
            except Exception:
                # This way it silences all thread level logging as well
                pass

        # Run in separate thread to have minimal overhead in main flows
        thread = threading.Thread(target=telemetry_logic, daemon=True)
        thread.start()
    except Exception:
        # Should never interfere with normal functions of Payserai
        pass
