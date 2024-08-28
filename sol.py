import random
import time
from collections import deque

# Constants
NUM_TAXI = 10
TAXI_SPEED = 40  # 20 meter per seconds
INTERVAL = 10  # 20 seconds
GRID = 20000  # 20,000 m


class Taxi:
    # States the taxi can be in
    STATE_STANDING = "standing"
    STATE_DRIVING_TO_START = "driving to start"
    STATE_DRIVING_TO_DESTINATION = "driving to destination"

    def __init__(self, taxi_id, x, y):
        self.id = taxi_id
        self.x = x
        self.y = y
        self.state = Taxi.STATE_STANDING
        self.destination = None  # where is the taxi headed
        self.ride_destination = None  # Final destination

    def __str__(self):
        return f"Taxi-{self.id}: {self.x / 1000:.1f}Km, {self.y / 1000:.1f}Km ({self.state})"

    def assign_ride(self, ride_request):
        # Assign new ride to the taxi
        self.state = Taxi.STATE_DRIVING_TO_START
        self.destination = ride_request.start
        self.ride_destination = ride_request.end

    def drive(self):
        if self.destination:
            x_des, y_des = self.destination
            # Update the taxi position
            if x_des != self.x:  # taxi is not in x destination
                step_x = min(INTERVAL * TAXI_SPEED, abs(self.x - x_des))  # calculate the step
                self.x += step_x if x_des > self.x else -step_x  # take the step

            remaining_time = INTERVAL - (abs(self.x - x_des) / TAXI_SPEED)  # calculate the remaining time to drive on y
            if remaining_time > 0:
                step_y = min(remaining_time * TAXI_SPEED, abs(self.y - y_des))
                self.y += step_y if y_des > self.y else -step_y

    def update_state(self):
        x_des, y_des = self.destination
        if self.x == x_des and self.y == y_des:  # update state only if taxi is in the destination
            if self.state == Taxi.STATE_DRIVING_TO_START:
                self.destination = self.ride_destination
                self.state = Taxi.STATE_DRIVING_TO_DESTINATION
            elif self.state == Taxi.STATE_DRIVING_TO_DESTINATION:
                self.state = Taxi.STATE_STANDING
                self.destination = None
                self.ride_destination = None


class RideRequest:
    def __init__(self, start_x, start_y, end_x, end_y):
        self.start = (start_x, start_y)
        self.end = (end_x, end_y)

    def __str__(self):
        return f"Ride from ({self.start[0] / 1000:.1f}Km, {self.start[1] / 1000:.1f}Km) to ({self.end[0] / 1000:.1f}Km, {self.end[1] / 1000:.1f}Km)"


class TaxiSimulation:
    def __init__(self):
        self.rides_queue = deque()  # hold the ride request
        self.taxis = []  # Initialize the list to hold the Taxis
        for i in range(NUM_TAXI):
            x = random.randint(0, GRID)
            y = random.randint(0, GRID)
            self.taxis.append(Taxi(i + 1, x, y))  # Add the taxi to the list

    def find_nearest_taxi(self, x_ride, y_ride):
        free_taxis = [taxi for taxi in self.taxis if taxi.state == Taxi.STATE_STANDING]  # array of standing taxis
        if not free_taxis:
            return None

        nearest_free_taxi = None
        min_distance = float('inf')  # Initialize large value

        for taxi in free_taxis:
            # Calculate Manhattan distance
            distance = abs(taxi.x - x_ride) + abs(taxi.y - y_ride)

            if distance < min_distance:
                min_distance = distance
                nearest_free_taxi = taxi

        return nearest_free_taxi

    def add_ride(self):
        # Create a new ride with random start and end points
        start_x = random.randint(0, GRID)
        start_y = random.randint(0, GRID)
        end_x = start_x + random.randint(-2000, 2000)
        end_y = start_y + random.randint(-2000, 2000)
        # make sure the point is within the grid
        end_x = max(0, min(GRID, end_x))
        end_y = max(0, min(GRID, end_y))

        ride = RideRequest(start_x, start_y, end_x, end_y)
        self.rides_queue.append(ride)
        print(f"New {ride}")

    def allocate_rides(self):
        # each ride in the queue to the nearest free taxi
        for request in list(
                self.rides_queue):  # iterate over a copy of the queue, avoid issues with modify the queue while iterate it.
            taxi = self.find_nearest_taxi(*request.start)
            if taxi:
                taxi.assign_ride(request)
                self.rides_queue.remove(request)
                print(f"Allocated {taxi} to {request}")

    def update_taxi(self):
        # update the position of each taxi that is currently driving
        for taxi in self.taxis:
            if taxi.state in [Taxi.STATE_DRIVING_TO_START, Taxi.STATE_DRIVING_TO_DESTINATION]:
                taxi.update_state()  # taxi is in the position of the pickup
                taxi.drive()
                taxi.update_state()
                self.leave_taxi()

    def leave_taxi(self):
        for taxi in self.taxis:
            if taxi.state in [Taxi.STATE_DRIVING_TO_DESTINATION]:
                rand_num = random.randint(0, 100)
                if rand_num < 20:
                    taxi.state = Taxi.STATE_STANDING
                    taxi.destination = None
                    taxi.ride_destination = None

    def print_status(self):
        print("\nOrder Queue:")
        if not self.rides_queue:
            print("Empty")
        else:
            for request in self.rides_queue:
                print(request)
        print("\nTaxi locations:")
        for taxi in self.taxis:
            print(taxi)

    def run(self):
        print("Taxi locations:")
        self.print_status()
        try:
            while True:
                time.sleep(INTERVAL)
                self.add_ride()
                self.allocate_rides()
                self.update_taxi()
                self.print_status()
        except KeyboardInterrupt:
            print("\nSimulation stopped. Have a nice ride :)")


if __name__ == '__main__':
    simulation = TaxiSimulation()
    simulation.run()
