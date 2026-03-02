# plcapp/signals.py
from django.dispatch import Signal

# Define a custom signal for PLC connection and value reading
menu_status = Signal()
