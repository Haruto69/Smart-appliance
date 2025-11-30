import lgpio

h = lgpio.gpiochip_open(0)
try:
    lgpio.gpio_claim_output(h, 0, 23, 0)
    print("✅ GPIO23 claimed successfully!")
    lgpio.gpio_free(h, 23)
except Exception as e:
    print("❌ Error claiming GPIO23:", e)
lgpio.gpiochip_close(h)
