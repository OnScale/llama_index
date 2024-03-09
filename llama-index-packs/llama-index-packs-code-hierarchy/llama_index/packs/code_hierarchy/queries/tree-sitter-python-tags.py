# Import statements
import math

# Global variable
PI = math.pi


# Function definition
def calculate_area(radius):
    """Calculates the area of a circle given its radius."""
    return PI * radius**2


# Class definition
class Circle:
    # Constructor method
    def __init__(self, radius: float) -> None:
        self.radius = radius

    # Instance method
    def area(self):
        """Calculates the area using the instance's radius."""
        return PI * self.radius**2

    # Static method
    @staticmethod
    def circumference(radius):
        """Calculates the circumference of a circle given its radius."""
        return 2 * PI * radius

    # Class method
    @classmethod
    def from_diameter(cls, diameter):
        """Creates a Circle instance from a diameter."""
        radius = diameter / 2
        return cls(radius)


# Inheritance example
class Cylinder(Circle):
    # Constructor method
    def __init__(self, radius: float, height: float) -> None:
        super().__init__(radius)
        self.height = height

    # Overriding method
    def area(self):
        """Calculates the surface area of the cylinder."""
        base_area = super().area()
        circumference = self.circumference(self.radius)
        side_area = circumference * self.height
        return 2 * base_area + side_area

    # New method
    def volume(self):
        """Calculates the volume of the cylinder."""
        base_area = super().area()
        return base_area * self.height


# Using a generator
def fibonacci_sequence(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


# Decorator example
def debug(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{func.__name__}({args}, {kwargs}) = {result}")
        return result

    return wrapper


@debug
def add(a: int, b: int) -> int:
    return a + b


# Main block to execute some examples
if __name__ == "__main__":
    circle = Circle(5)
    print(f"Circle area: {circle.area()}")
    cylinder = Cylinder(5, 10)
    print(f"Cylinder area: {cylinder.area()}")
    print(f"Cylinder volume: {cylinder.volume()}")

    fib_seq = list(fibonacci_sequence(10))
    print(f"Fibonacci sequence (first 10 numbers): {fib_seq}")

    sum_result = add(5, 3)
    print(f"Sum of 5 and 3: {sum_result}")
