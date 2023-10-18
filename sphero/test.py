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

TOY_NAME = "SB-2D08"


class Sphero:
    def __init__(self):
        signal.signal(signal.SIGUSR1, lambda signal, frame: self._USR1_signal_handler())
        signal.signal(signal.SIGUSR2, lambda signal, frame: self._USR2_signal_handler())

        self.toy = None
        self.stopSphero = False

        self.SPEED = 50
        self.ONE_SIDE = 45  # one side of the square in cms

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

    def _USR1_signal_handler(self):
        self.stopSphero = True

    def _USR2_signal_handler(self):
        self.stopSphero = False

    def on_collision(api):
        print("Collision!!!!")

    def MainLoop(self, count=-1):
        if self.toy is None:
            print("Could not find the Sphero")
            exit(-1)

        def move(bolt, heading, distance):
            init_distance = d = bolt.get_distance()
            while d < (init_distance + distance):
                bolt.roll(heading, self.SPEED, 0.0001)
                d = bolt.get_distance()
            time.sleep(2)
            print(
                f"{heading}: init - {init_distance}; final - {d}. Total = {d - init_distance}"
            )

        with SpheroEduAPI(self.toy) as bolt:
            bolt.reset_aim()
            bolt.set_stabilization(True)
            bolt.set_front_led(Color(239, 0, 255))
            bolt.register_event(EventType.on_collision, self.on_collision)
            bolt.set_main_led(Color(r=0, g=255, b=0))

            print(f"Starting Distance: {bolt.get_distance()}")

            if count < 0:
                while True:
                    move(bolt, 0, self.ONE_SIDE)
                    move(bolt, 90, self.ONE_SIDE)
                    move(bolt, 180, self.ONE_SIDE)
                    move(bolt, 270, self.ONE_SIDE)

            else:
                for i in range(count):
                    print(f"loop: {i}")
                    move(bolt, 0, self.ONE_SIDE)
                    move(bolt, 90, self.ONE_SIDE)
                    move(bolt, 180, self.ONE_SIDE)
                    move(bolt, 270, self.ONE_SIDE)

            # reset bolt heading
            bolt.roll(0, self.SPEED, 0)
            time.sleep(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="SpheroDriver",
        description="Run a Sphero in a square loop",
    )
    parser.add_argument(
        "--count", type=int, default=-1, help="loop count. -1 means forever."
    )
    args = parser.parse_args()
    print(args)
    app = Sphero()
    # app.MainLoop(args.count)
    with SpheroEduAPI(app.toy) as bolt:
        bolt.reset_aim()
        bolt.set_stabilization(True)
        bolt.set_front_led(Color(239, 0, 255))
        bolt.register_event(EventType.on_collision, app.on_collision)
        bolt.set_main_led(Color(r=0, g=255, b=0))
        bolt.roll(0, -app.SPEED, 5)
