# IoT Hardware Telemetry & Shrinkage Forensics

## 1. Supported Peripherals
1. **Optical 1D/2D Barcode Laser Scanners**: Decodes UPC-A, EAN-13, and Code-128 symbologies via RS232 or USB-HID emulation.
2. **UHF RFID Archway Portal Gateways**: Interrogates EPC Gen2 Class 1 passive RFID tags across 860-960 MHz bands at inbound receiving gates.
3. **Smart Weighing Shelf RS232 Scales**: Precision load-cell bench scales monitoring high-shrinkage pick-zone bins.

## 2. Shrinkage Detection Algorithm
```python
def evaluate_shrinkage(measured_weight_kg, unit_weight_kg, database_quantity):
    calculated_quantity = int(round(measured_weight_kg / unit_weight_kg))
    discrepancy = calculated_quantity - database_quantity
    
    if discrepancy == 0:
        return "MATCH", 0
    elif discrepancy < 0:
        # Physical units missing (shrinkage, unrecorded loss, theft)
        return "DEFICIT", discrepancy
    else:
        # Untracked intake on shelf
        return "SURPLUS", discrepancy
```
