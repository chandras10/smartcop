import time
from spherov2 import scanner
from spherov2.sphero_edu import SpheroEduAPI, EventType
from spherov2.types import Color
from spherov2.adapter.tcp_adapter import get_tcp_adapter
from spherov2.commands.sphero import RollModes
from spherov2.scanner import ToyNotFoundError
import signal

TOY_NAME = "SB-2D08"


class Sphero:
    def __init__(self):
        signal.signal(signal.SIGUSR1, lambda signal, frame: self._USR1_signal_handler())
        signal.signal(signal.SIGUSR2, lambda signal, frame: self._USR2_signal_handler())

        self.stopSphero = False
        self.MAX_STEPS = 3
        self.SPEED = 50
        self.curr_step = 0
        self.toy = None

    def _USR1_signal_handler(self):
        self.stopSphero = True

    def _USR2_signal_handler(self):
        self.stopSphero = False

    def on_collision(api):
        print("Collision!!!!")

    def MainLoop(self):
        for retry in range(2):
            try:
                self.toy = scanner.find_toy(toy_name=TOY_NAME)
                break
            except ToyNotFoundError:
                print("Trying to find the sphero...")
                pass

        if not self.toy:
            print("Could not find the Sphero")
            exit(-1)

        self.toy.name = "Chandra's Sphero"
        print(self.toy)

        with SpheroEduAPI(self.toy) as bolt:
            bolt.register_event(EventType.on_collision, self.on_collision)
            bolt.set_heading(0)
            self.curr_step = 0
            while True:
                if self.stopSphero:
                    bolt.set_speed(0)
                    bolt.set_main_led(Color(r=255, g=0, b=0))
                    continue

                bolt.set_main_led(Color(r=0, g=255, b=0))
                h = bolt.get_heading()
                if h == 0:
                    bolt.roll(270, self.SPEED, 0.25)
                    bolt.roll(0, self.SPEED, 0.25)
                    time.sleep(1)
                step_count = self.MAX_STEPS - self.curr_step
                if step_count < 0:
                    step_count = bolt.MAX_STEPS
                for i in range(step_count):
                    bolt.roll(h, self.SPEED, 1)
                    self.curr_step += 1
                    if self.stopSphero:
                        break
                if not self.stopSphero:
                    bolt.set_heading(h + 90)
                    self.curr_step = 0
                time.sleep(1)


if __name__ == "__main__":
    app = Sphero()
    app.MainLoop()
