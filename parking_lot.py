import heapq
import unittest
from datetime import datetime, timedelta
from enum import Enum
from math import ceil


class VehicleType(Enum):
    BIKE = "BIKE"
    CAR = "CAR"
    TRUCK = "TRUCK"


RATE_PER_HOUR = {
    VehicleType.BIKE: 50,
    VehicleType.CAR: 100,
    VehicleType.TRUCK: 200,
}

# Index 0 = Slot 1, index 1 = Slot 2, ...
SLOT_LAYOUT = [
    VehicleType.BIKE, VehicleType.BIKE,
    VehicleType.CAR, VehicleType.CAR, VehicleType.CAR,
    VehicleType.TRUCK, VehicleType.TRUCK,
    VehicleType.CAR, VehicleType.CAR,
    VehicleType.TRUCK,
]


class Vehicle:
    def __init__(self, number, vehicle_type):
        self.number = number
        self.vehicle_type = vehicle_type


class Slot:
    def __init__(self, number, vehicle_type):
        self.number = number
        self.vehicle_type = vehicle_type  # the only type this slot accepts
        self.vehicle = None               # None means the slot is empty


class Ticket:
    def __init__(self, ticket_id, vehicle, slot, entry_time):
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.slot = slot
        self.entry_time = entry_time


class ParkingLot:
    def __init__(self, layout=SLOT_LAYOUT):
        self.slots = [Slot(i + 1, t) for i, t in enumerate(layout)]
        self.active_tickets = {}  # vehicle number -> Ticket
        self.next_ticket_id = 1

        # One min-heap of free slot numbers per vehicle type.
        # heap is always the lowest free slot for that type.
        self.free_slots = {t: [] for t in VehicleType}
        for slot in self.slots:
            heapq.heappush(self.free_slots[slot.vehicle_type], slot.number)

    def park_vehicle(self, number, vehicle_type, entry_time=None):
        if number in self.active_tickets:
            raise ValueError(f"{number} already parked")

        heap = self.free_slots[vehicle_type]
        if not heap:
            raise ValueError("No suitable parking slot available")

        slot_number = heapq.heappop(heap)  # lowest free slot of this type
        slot = self.slots[slot_number - 1]

        vehicle = Vehicle(number, vehicle_type)
        slot.vehicle = vehicle

        ticket = Ticket(self.next_ticket_id, vehicle, slot, entry_time or datetime.now())
        self.next_ticket_id += 1
        self.active_tickets[number] = ticket

        print(f"{number} -> Slot {slot.number} (Ticket #{ticket.ticket_id})")
        return ticket

    def leave_vehicle(self, number, exit_time=None):
        ticket = self.active_tickets.pop(number, None)
        if ticket is None:
            raise ValueError("Vehicle not found")

        exit_time = exit_time or datetime.now()
        fee = self._calculate_fee(ticket, exit_time)

        # Free the slot and return it to the heap so it can be reused
        slot = ticket.slot
        slot.vehicle = None
        heapq.heappush(self.free_slots[slot.vehicle_type], slot.number)

        print(f"--- Receipt ---
"
              f"Ticket #{ticket.ticket_id} | {number} | Slot {slot.number}
"
              f"In: {ticket.entry_time:%H:%M}  Out: {exit_time:%H:%M}
"
              f"Fee: Rs.{fee}
"
              f"---------------")
        return fee

    def _calculate_fee(self, ticket, exit_time):
        seconds = (exit_time - ticket.entry_time).total_seconds()
        hours = max(1, ceil(seconds / 3600))  # any started hour is a full hour
        return hours * RATE_PER_HOUR[ticket.vehicle.vehicle_type]

    def get_parking_status(self):
        lines = []
        for slot in self.slots:
            if slot.vehicle is None:
                lines.append(f"Slot {slot.number} -> EMPTY")
            else:
                v = slot.vehicle
                lines.append(f"Slot {slot.number} -> {v.vehicle_type.value} -> {v.number}")
        return "
".join(lines)

    def find_vehicle(self, number):
        ticket = self.active_tickets.get(number)
        if ticket is None:
            raise ValueError("Vehicle not found")
        return ticket.slot.number


# ------------------------------- Tests -------------------------------

class ParkingLotTest(unittest.TestCase):
    def setUp(self):
        self.lot = ParkingLot()
        self.t0 = datetime(2026, 1, 1, 10, 0)

    def test_lowest_slot_assigned(self):
        self.lot.park_vehicle("B1", VehicleType.BIKE, self.t0)
        self.lot.park_vehicle("C1", VehicleType.CAR, self.t0)
        self.lot.park_vehicle("T1", VehicleType.TRUCK, self.t0)
        self.assertEqual(self.lot.find_vehicle("B1"), 1)
        self.assertEqual(self.lot.find_vehicle("C1"), 3)
        self.assertEqual(self.lot.find_vehicle("T1"), 6)

    def test_duplicate_entry(self):
        self.lot.park_vehicle("C1", VehicleType.CAR, self.t0)
        with self.assertRaisesRegex(ValueError, "already parked"):
            self.lot.park_vehicle("C1", VehicleType.CAR, self.t0)

    def test_no_suitable_slot(self):
        self.lot.park_vehicle("B1", VehicleType.BIKE, self.t0)
        self.lot.park_vehicle("B2", VehicleType.BIKE, self.t0)
        with self.assertRaisesRegex(ValueError, "No suitable parking slot"):
            self.lot.park_vehicle("B3", VehicleType.BIKE, self.t0)  # bike never takes car/truck slots

    def test_leave_unknown_vehicle(self):
        with self.assertRaisesRegex(ValueError, "Vehicle not found"):
            self.lot.leave_vehicle("NOPE")

    def test_fee_rounds_up_started_hour(self):
        self.lot.park_vehicle("C1", VehicleType.CAR, self.t0)
        fee = self.lot.leave_vehicle("C1", self.t0 + timedelta(hours=2, minutes=10))
        self.assertEqual(fee, 300)

    def test_slot_reused_after_leaving(self):
        self.lot.park_vehicle("C1", VehicleType.CAR, self.t0)
        self.lot.park_vehicle("C2", VehicleType.CAR, self.t0)
        self.lot.leave_vehicle("C1", self.t0 + timedelta(hours=1))
        self.lot.park_vehicle("C3", VehicleType.CAR, self.t0)
        self.assertEqual(self.lot.find_vehicle("C3"), 3)  # slot 3 is free again


if __name__ == "__main__":
    lot = ParkingLot()
    lot.park_vehicle("BWP-123", VehicleType.BIKE)
    lot.park_vehicle("LEA-456", VehicleType.CAR)
    lot.park_vehicle("ISB-789", VehicleType.TRUCK)
    print(lot.get_parking_status())

    lot.leave_vehicle("LEA-456")
    print(lot.get_parking_status())

    unittest.main()