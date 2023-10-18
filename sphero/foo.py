class A:
    V = "Hello"

    def createB(self):
        return A.B(self)

    class B(object):
        def __init__(self, outer):
            self.outer = outer

        def move(self, i):
            method_name = "move_" + str(i)
            method = getattr(self, method_name, lambda: "not a proper heading")
            return method()

        def move_0(self):
            print(f"Moving...0 {self.outer.V}")

        def move_1(self):
            print(f"Moving...1 {self.outer.V}")


a = A()
a.createB().move(0)
a.createB().move(1)
