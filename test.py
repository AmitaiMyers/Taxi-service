import unittest
from sol import Taxi, RideRequest, TaxiSimulation

TAXI_SPEED = 20  # 20 meters per second
INTERVAL = 20  # 20 seconds
STEP = INTERVAL * TAXI_SPEED


class TestTaxi(unittest.TestCase):

    def test_initial_state(self):  # create taxi
        taxi = Taxi(1, 1000, 1000)
        self.assertEqual(taxi.state, Taxi.STATE_STANDING)
        self.assertIsNone(taxi.destination)
        self.assertIsNone(taxi.ride_destination)

    def test_assign_ride(self):  # assign ride
        taxi = Taxi(1, 1000, 1000)
        ride = RideRequest(2000, 2000, 3000, 3000)
        taxi.assign_ride(ride)
        self.assertEqual(taxi.state, Taxi.STATE_DRIVING_TO_START)
        self.assertEqual(taxi.destination, ride.start)
        self.assertEqual(taxi.ride_destination, ride.end)

    def test_drive_to_start_x(self):  # one interval drive in x direction
        taxi = Taxi(1, 1000, 1000)
        ride = RideRequest(2000, 1000, 3000, 3000)
        taxi.assign_ride(ride)
        taxi.drive()
        self.assertEqual(taxi.x, 1000 + STEP)
        self.assertEqual(taxi.y, 1000)
        self.assertEqual(taxi.state, Taxi.STATE_DRIVING_TO_START)

    def test_drive_to_start_y(self):  # one interval drive in y direction
        taxi = Taxi(1, 1000, 1000)
        ride = RideRequest(1000, 1800, 3000, 3000)
        taxi.assign_ride(ride)
        taxi.drive()
        self.assertEqual(taxi.x, 1000)
        self.assertEqual(taxi.y, 1000 + STEP)
        self.assertEqual(taxi.state, Taxi.STATE_DRIVING_TO_START)

    def test_drive_to_destination(self):  # taxi is in the pickup point, 2 intervals
        taxi = Taxi(1, 2000, 1000)
        ride = RideRequest(2000, 1000, 3000, 2000)
        taxi.assign_ride(ride)
        taxi.drive()  # Move towards the start point
        taxi.update_state()  # Check if taxi is at the start point
        self.assertEqual(taxi.state, Taxi.STATE_DRIVING_TO_DESTINATION)
        taxi.drive()  # Move towards the destination
        self.assertEqual(taxi.x, 2000 + STEP)
        self.assertEqual(taxi.y, 1000)

    def test_arrival(self):  # Taxi arrives at the destination
        taxi = Taxi(1, 1000, 1000)
        ride = RideRequest(1000, 1000, 1200, 1000)
        taxi.assign_ride(ride)
        taxi.drive()  # Move to the start point
        taxi.update_state()  # Check if taxi is at the start point
        taxi.drive()  # Move to the destination
        taxi.update_state()  # Check if taxi has arrived
        self.assertEqual(taxi.state, Taxi.STATE_STANDING)
        self.assertIsNone(taxi.destination)
        self.assertIsNone(taxi.ride_destination)

    def test_no_movement_needed(self):  # Test when taxi is already at the start point
        taxi = Taxi(1, 2000, 2000)
        ride = RideRequest(2000, 2000, 3000, 3000)
        taxi.assign_ride(ride)
        taxi.update_state()  # Should transition to driving to destination immediately
        self.assertEqual(taxi.state, Taxi.STATE_DRIVING_TO_DESTINATION)
        self.assertEqual(taxi.x, 2000)
        self.assertEqual(taxi.y, 2000)

    def test_partial_movement(self):  # Test partial movement when destination is close
        taxi = Taxi(1, 1000, 1000)
        ride = RideRequest(1100, 1000, 1200, 1000)
        taxi.assign_ride(ride)
        taxi.drive()  # Should move 100 meters to 1100, 1000
        self.assertEqual(taxi.x, 1100)
        self.assertEqual(taxi.y, 1000)
        taxi.update_state()  # Now driving to final destination
        taxi.drive()  # Should move 100 more meters to 1200, 1000
        self.assertEqual(taxi.x, 1200)
        self.assertEqual(taxi.y, 1000)

    def test_return_to_standing(self):  # Test that taxi returns to standing after completing a ride
        taxi = Taxi(1, 1000, 1000)
        ride = RideRequest(1000, 1000, 1400, 1000)
        self.assertEqual(taxi.state, Taxi.STATE_STANDING)
        taxi.assign_ride(ride)
        self.assertEqual(taxi.state, Taxi.STATE_DRIVING_TO_START)
        taxi.update_state()  # change to drive to destination
        self.assertEqual(taxi.state, Taxi.STATE_DRIVING_TO_DESTINATION)
        taxi.drive()  # Move to the start point
        taxi.update_state()  # Should be standing now
        self.assertEqual(taxi.state, Taxi.STATE_STANDING)
        self.assertIsNone(taxi.destination)
        self.assertIsNone(taxi.ride_destination)


class TestTaxiSimulation(unittest.TestCase):

    def setUp(self):
        self.simulation = TaxiSimulation()

    def test_add_ride(self):
        self.simulation.add_ride()
        self.assertEqual(len(self.simulation.rides_queue), 1)

    def test_allocate_rides(self):
        self.simulation.add_ride()
        self.simulation.allocate_rides()
        self.assertEqual(len(self.simulation.rides_queue), 0)

    def test_allocate_rides_no_taxis_available(self):
        # Simulate all taxis being busy
        for taxi in self.simulation.taxis:
            taxi.state = Taxi.STATE_DRIVING_TO_DESTINATION
        self.simulation.add_ride()
        self.simulation.allocate_rides()
        self.assertEqual(len(self.simulation.rides_queue), 1)

    def test_update_taxi(self):
        self.simulation.add_ride()
        self.simulation.allocate_rides()
        self.simulation.update_taxi()
        for taxi in self.simulation.taxis:
            if taxi.state == Taxi.STATE_DRIVING_TO_START or taxi.state == Taxi.STATE_DRIVING_TO_DESTINATION:
                self.assertTrue(taxi.x != taxi.destination[0] or taxi.y != taxi.destination[1])


if __name__ == '__main__':
    unittest.main()
