// TypeScript Example showcasing various language structures

// Interface definition
interface Shape {
  getArea(): number;
}

// Class definition
class Circle implements Shape {
  radius: number;

  // Constructor
  constructor(radius: number) {
    this.radius = radius;
  }

  // Method implementing the Shape interface
  getArea(): number {
    return Math.PI * this.radius ** 2;
  }

  // Static method
  static calculateArea(radius: number): number {
    return Math.PI * radius ** 2;
  }
}

// Inheritance
class Cylinder extends Circle {
  height: number;

  // Constructor
  constructor(radius: number, height: number) {
    super(radius); // Call the superclass constructor
    this.height = height;
  }

  // Overriding method
  getArea(): number {
    // Surface area of the cylinder
    return 2 * Math.PI * this.radius * this.height + 2 * super.getArea();
  }

  // New method specific to Cylinder
  getVolume(): number {
    return super.getArea() * this.height;
  }
}

// Enum example
enum Day {
  Monday,
  Tuesday,
  Wednesday,
  Thursday,
  Friday,
  Saturday,
  Sunday,
}

// Generic function
function printArray<T>(array: T[]): void {
  console.log(array.join(", "));
}

// Main block
(() => {
  const circle: Circle = new Circle(5);
  console.log("Circle area:", circle.getArea());

  const cylinder: Cylinder = new Cylinder(5, 10);
  console.log("Cylinder area:", cylinder.getArea());
  console.log("Cylinder volume:", cylinder.getVolume());

  // Using enum
  const today: Day = Day.Monday;
  console.log("Today is:", Day[today]);

  // Using generics
  printArray<number>([1, 2, 3, 4, 5]);
  printArray<string>(["Hello", "TypeScript"]);
})();
