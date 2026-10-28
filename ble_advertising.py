import ustruct
import bluetooth

_ADV_TYPE_FLAGS = 0x01
_ADV_TYPE_NAME = 0x09

def advertising_payload(name=None, services=None):
    payload = bytearray()

    def _append(adv_type, value):
        payload.extend(ustruct.pack("BB", len(value) + 1, adv_type) + value)

    _append(_ADV_TYPE_FLAGS, b"\x06")

    if name:
        _append(_ADV_TYPE_NAME, name.encode())

    return payload