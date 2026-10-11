# Parking Lot Management System

A robust, object-oriented Python implementation of an automated parking vehicle manager. The system tracks various vehicle profiles (Bikes, Cars, Trucks), dynamically optimizes parking space configurations, calculates hourly ticketing metrics, and validates functions via integrated unit tests.

## Key Architecture & Features
- **Optimal Space Allocation:** Leverages Min-Heaps (`heapq`) to automatically assign arriving vehicles to the lowest available slot number matching their size type.
- **Dynamic Fee Calculator:** Automatically tracks runtime hours, rounding up fractional times to evaluate tiered hourly structures based on vehicle classification.
- **Robust Test Coverage:** Integrated `unittest` suites thoroughly evaluate constraints like double entries, exhausted capacities, and billing accuracy.

## How to Run
Ensure you have Python 3 installed. You can execute the code and run the system simulation directly through your terminal:

```bash
python parking_lot.py
```
