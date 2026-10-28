from machine import Pin, ADC, I2C, PWM
import ssd1306
import time

from wifi_alert import WiFiAlert
# -------------------

# -------------------
last_alert_state = None

# -------------------
# MQ-2 SENSOR
# -------------------
mq2 = ADC(Pin(3))
mq2.atten(ADC.ATTN_11DB)

# -------------------
# OUTPUTS
# -------------------
red_led = Pin(6, Pin.OUT)     # DANGER
blue_led = Pin(2, Pin.OUT)    # WARNING
green_led = Pin(8, Pin.OUT)   # SAFE

buzzer = PWM(Pin(0))
buzzer.duty(0)

wifi = WiFiAlert(
    "Malibu",
    "TimoN2005",
    "8549596077:AAFyQdPuH5qOIOi3R97e4qMFAQjFrWm-7ok",
    "8749997862"
)

wifi.connect()

# -------------------
# OLED DISPLAY
# -------------------
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# -------------------
# FUNCTIONS
# -------------------
def beep(freq=1000, duty=512):
    buzzer.freq(freq)
    buzzer.duty(duty)

def silent():
    buzzer.duty(0)

def get_status(percent):
    if percent < 4:
        return "SAFE"
    elif percent < 10:
        return "WARNING"
    else:
        return "DANGER"

def to_percent(value):
    return int((value / 4095) * 100)

def read_avg(samples=5):
    total = 0
    for _ in range(samples):
        total += mq2.read()
        time.sleep(0.01)
    return total // samples

# -------------------
# STATE TRACKING
# -------------------
last_status = None
last_sent_time = 0

# -------------------
# WARM-UP SCREEN
# -------------------
warmup_time = 20

for i in range(warmup_time, 0, -1):
    oled.fill(0)
    oled.text("GAS MONITOR", 0, 0)
    oled.text("Warming MQ2 ", 0, 20)
    oled.text("Sensor...", 0, 35)
    oled.text("Wait: {}s".format(i), 0, 50)
    oled.show()
    time.sleep(1)

# -------------------
# MAIN LOOP
# -------------------
try:
    while True:
        
        raw = read_avg()
        percent = to_percent(raw)
        status = get_status(percent)

        print("Gas:", percent, "% |", status)

        # ---------------- BLE LOGIC ----------------
        current_time = time.time()
        if status == "DANGER" and last_alert_state != "DANGER":
            
            wifi.send("🚨 GAS LEAK DETECTED! EVACUATE IMMEDIATELY!")
            
            last_alert_state = "DANGER"
            

        elif status != "DANGER":
            
            last_alert_state = status

        elif current_time - last_sent_time > 10:
            wifi.send("Gas:{}%".format(percent))
            last_sent_time = current_time
        



        # ---------------- OLED ----------------
        oled.fill(0)
        oled.text("GAS MONITOR", 0, 0)
        oled.text("Value: {}%".format(percent), 0, 20)
        oled.text("Status: {}".format(status), 0, 40)
        oled.show()

        # ---------------- LED RESET ----------------
        red_led.value(0)
        blue_led.value(0)
        green_led.value(0)

        # ---------------- ALERT LOGIC ----------------
        if status == "SAFE":
            green_led.value(1)
            silent()
            time.sleep(0.5)

        elif status == "WARNING":
            blue_led.value(1)

            # slow beep
            beep(700)
            time.sleep(0.2)
            silent()
            time.sleep(1.2)

        else:  # DANGER
            beep(1500)

            # alternating LEDs
            red_led.value(1)
            time.sleep(0.2)
            red_led.value(0)

            blue_led.value(1)
            time.sleep(0.2)
            blue_led.value(0)

except KeyboardInterrupt:
    pass

finally:
    silent()

    red_led.value(0)
    blue_led.value(0)
    green_led.value(0)

    oled.fill(0)
    oled.text("System", 20, 20)
    oled.text("Shut down", 20, 40)
    oled.show()