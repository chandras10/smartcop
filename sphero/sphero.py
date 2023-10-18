import time
from spherov2 import scanner
from spherov2.sphero_edu import SpheroEduAPI, EventType
from spherov2.types import Color
from spherov2.adapter.tcp_adapter import get_tcp_adapter
from spherov2.commands.sphero import RollModes
from spherov2.scanner import ToyNotFoundError
from spherov2.types import Color
import signal
import argparse
import os
import collections
from enum import Enum
import inspect

DEBUG = False

TOY_NAME = "SB-2D08"

def DebugMessage(s: str):
    if DEBUG:
        print(s)

class Heading_Direction(Enum):
    TOP = 0
    RIGHT = 90
    BOTTOM = 180
    LEFT = 270


class Sphero:
    COORDS = {
        0: {"x": 0.0, "y": 60.0},
        90: {"x": 40.0, "y": 60.0},
        180: {"x": 40.0, "y": 0.0},
        270: {"x": 0.0, "y": 0.0},
    }
    SPEED = 50
    STEP_TIME = 0.0001  # Time Interval (fractions of seconds) to roll the sphero at certain speed

    # This buffer is used to save the most recent N (x,y) positions to decide if the Sphero is stuck or moving.
    BUFFER_LENGTH = 20

    class move_toy(object):
        def __init__(self, outer, bolt):
            self.outer = outer
            self.bolt = bolt

        def move(self):
            if self.outer.is_toy_stuck or self.outer.is_stopped:
                return

            heading = Heading_Direction(self.outer.heading).name
            method_name = "heading_towards_" + heading
            method = getattr(
                self,
                method_name,
                lambda: "not a proper heading value. Should be one of [0,90,180,270]",
            )
            method()
            time.sleep(1)

            if DEBUG:
                print(f"Moved to {heading} position")

        # fmt: off
        def heading_towards_TOP(self):
            while self.outer.trail[1][0] < self.outer.COORDS[0]["y"]:
                DebugMessage(f"{inspect.currentframe().f_code.co_name} - ({self.outer.trail[0][0]}, {self.outer.trail[1][0]})")
                if self.outer.is_toy_stuck:
                    break
                self.bolt.roll(0, self.outer.SPEED, self.outer.STEP_TIME)
            self.bolt.stop_roll()

        def heading_towards_RIGHT(self):
            while self.outer.trail[0][0] < self.outer.COORDS[90]["x"]:
                DebugMessage(f"{inspect.currentframe().f_code.co_name} - ({self.outer.trail[0][0]}, {self.outer.trail[1][0]})")
                if self.outer.is_toy_stuck:
                    break
                self.bolt.roll(90, self.outer.SPEED, self.outer.STEP_TIME)
            self.bolt.stop_roll()

        def heading_towards_BOTTOM(self):
            while self.outer.trail[1][0] > self.outer.COORDS[180]["y"]:
                DebugMessage(f"{inspect.currentframe().f_code.co_name} - ({self.outer.trail[0][0]}, {self.outer.trail[1][0]})")
                if self.outer.is_toy_stuck:
                    break
                self.bolt.roll(180, self.outer.SPEED, self.outer.STEP_TIME)
            self.bolt.stop_roll()

        def heading_towards_LEFT(self):
            while self.outer.trail[0][0] > self.outer.COORDS[270]["x"]:
                DebugMessage(f"{inspect.currentframe().f_code.co_name} - ({self.outer.trail[0][0]}, {self.outer.trail[1][0]})")
                if self.outer.is_toy_stuck:
                    break
                self.bolt.roll(270, self.outer.SPEED, self.outer.STEP_TIME)
            self.bolt.stop_roll()

    def __init__(self):

        self.INIT_BUFFER = []
        for i in range(self.BUFFER_LENGTH):
            self.INIT_BUFFER.append(i + 1)

        # Using two buffers to store the X and Y positions in the 2D space that the sphero moves in
        # These buffers will save the most recent N values and will decide if the Sphero is stuck or moving.
        self.trail = [
            collections.deque(self.INIT_BUFFER, maxlen=self.BUFFER_LENGTH),
            collections.deque(self.INIT_BUFFER, maxlen=self.BUFFER_LENGTH),
        ]

        self.toy = None
        self.heading = 0
        self.is_toy_stuck = False

        for retry in range(2):
            try:
                self.toy = scanner.find_toy(toy_name=TOY_NAME)
                break
            except ToyNotFoundError:
                print("Trying to find the sphero...")
                pass

        if self.toy:
            self.toy.name = "Chandra's Sphero"
            print(self.toy)

        self.is_stopped = False
        signal.signal(signal.SIGUSR1, lambda signal, frame: self.stop_moving())
        signal.signal(signal.SIGUSR2, lambda signal, frame: self.resume_moving())

    def on_streaming_data(self, api):
        DebugMessage(f"{self.heading}: {api._SpheroEduAPI__sensor_data['locator']}")

        # print(f"""distance: {api._SpheroEduAPI__sensor_data['distance']},\n
        #        roll: {api._SpheroEduAPI__sensor_data['attitude']['roll']},\n
        #        location: {api._SpheroEduAPI__sensor_data['locator']}\n\n\n
        #        """
        #     )
        try:
            if self.is_toy_stuck:
                return

            # First element will always have the latest position of the Sphero
            self.trail[0].appendleft(round(api._SpheroEduAPI__sensor_data["locator"]["x"], 1))
            self.trail[1].appendleft(round(api._SpheroEduAPI__sensor_data["locator"]["y"], 1))

            if self.is_stopped:
                return

            # Is the Sphero moving in horizontal or vertical direction?
            if self.heading == Heading_Direction.LEFT.value or self.heading == Heading_Direction.RIGHT.value:
                if len(set(self.trail[1])) > 1:
                    return
                DebugMessage(f"STUCK!!!! STUCK!!!! STUCK!!!! STUCK @ header: {Heading_Direction(self.heading).name}")
                self.is_toy_stuck = True
            else:  # Moving TOP/DOWN
                if len(set(self.trail[0])) > 1:
                    return
                DebugMessage(f"STUCK!!!! STUCK!!!! STUCK!!!! STUCK @ header: {Heading_Direction(self.heading).name}")
                self.is_toy_stuck = True

        except ValueError:
            self.is_stopped = True
            pass  # Getting those nasty NaN sometimes...

    def on_collision(self, api):
        print("collision!!!!")

    def stop_moving(self):
        self.is_stopped = True

    def resume_moving(self):
        self.is_stopped = False
        self.reset_buffer()
        self.is_toy_stuck = False

    def reset_buffer(self):
        self.trail[0].clear()
        self.trail[0].extend(self.INIT_BUFFER)
        self.trail[1].clear()
        self.trail[1].extend(self.INIT_BUFFER)

    def MainLoop(self, loop_count=-1):
        if self.toy is None:
            print("Could not find the Sphero")
            exit(-1)

        with SpheroEduAPI(self.toy) as bolt:
            bolt.reset_aim()
            bolt.set_stabilization(True)
            bolt.set_front_led(Color(239, 0, 255))
            bolt.set_main_led(Color(r=0, g=255, b=0))

            bolt.register_event(EventType.on_sensor_streaming_data, self.on_streaming_data)
            bolt.register_event(EventType.on_collision, self.on_collision)

            count = 0
            _run = True
            while _run:
                if self.is_stopped:
                    time.sleep(1)
                    DebugMessage("STOPPED")
                    continue

                if self.is_toy_stuck:
                    self.heading = (self.heading + 90) % 360
                    self.reset_buffer()
                    self.is_toy_stuck = False

                # Keep going in circles (or rather squares)...
                while not self.is_toy_stuck:
                    if self.is_stopped:
                        break

                    self.move_toy(self, bolt).move()
                    if not self.is_toy_stuck:
                        self.heading = (self.heading + 90) % 360
                    # Do we loop infinitely or for finite count?
                    if loop_count > 0 and self.heading == 0:
                        count += 1
                        if count >= loop_count:
                            _run = False
                            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="SpheroDriver",
        description="Run a Sphero in a square loop",
    )
    parser.add_argument(
        "--count", type=int, default=-1, help="loop count. -1 means forever(default)."
    )
    args = parser.parse_args()

    app = Sphero()
    app.MainLoop(args.count)
