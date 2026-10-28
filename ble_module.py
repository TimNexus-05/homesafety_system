# ble_module.py

import bluetooth
from ble_advertising import advertising_payload

class BLEMQ2:
    def __init__(self, name="MQ2-SENSOR"):
        self.ble = bluetooth.BLE()
        self.ble.active(True)

        self.SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
        self.CHAR_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

        service = (
            self.SERVICE_UUID,
            ((self.CHAR_UUID, bluetooth.FLAG_NOTIFY),),
        )

        ((self.char_handle,),) = self.ble.gatts_register_services((service,))

        self.connections = set()
        self.ble.irq(self._irq)

        self._advertise(name)

    def _irq(self, event, data):
        if event == 1:  # CONNECT
            conn_handle, _, _ = data
            self.connections.add(conn_handle)

        elif event == 2:  # DISCONNECT
            conn_handle, _, _ = data
            self.connections.remove(conn_handle)
            self._advertise("MQ2-SENSOR")

    def _advertise(self, name):
        payload = advertising_payload(name=name)
        self.ble.gap_advertise(100, payload)
        print("BLE advertising...")

    def send(self, message):
        for conn in self.connections:
            self.ble.gatts_notify(conn, self.char_handle, message)