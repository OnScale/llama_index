## 1041c8a8-ddfd-4583-bed1-dd063c7d6b2c

```javascript
// JavaScript Example showcasing various language structures

// Class definition
class Circle {
  constructor(radius) {
    this.radius = radius;
  }

  // Method
  getArea() {
    return Math.PI * this.radius ** 2;
  }

  // Static method
  static calculateArea(radius) {
    return Math.PI * radius ** 2;
  }
}

// Inheritance
class Cylinder extends Circle {
  constructor(radius, height) {
    super(radius); // Call the superclass constructor
    this.height = height;
  }

  // Overriding method
  getArea() {
    // Surface area of the cylinder
    return 2 * Math.PI * this.radius * this.height + 2 * super.getArea();
  }

  // New method specific to Cylinder
  getVolume() {
    return super.getArea() * this.height;
  }
}

// Function
function calculateVolume(radius, height) {
  let circle = new Circle(radius);
  return circle.getArea() * height;
}

// Arrow function
const calculateCircumference = (radius) => {
  return 2 * Math.PI * radius;
};

// Using an array and map function
const numbers = [1, 2, 3, 4, 5];
const squares = numbers.map((number) => number ** 2);

// IIFE (Immediately Invoked Function Expression)
(() => {
  console.log("This code runs immediately upon definition.");
})();

// Main block
(() => {
  const circle = new Circle(5);
  console.log("Circle area:", circle.getArea());

  const cylinder = new Cylinder(5, 10);
  console.log("Cylinder area:", cylinder.getArea());
  console.log("Cylinder volume:", cylinder.getVolume());

  console.log("Volume (function):", calculateVolume(5, 10));
  console.log("Circumference (arrow function):", calculateCircumference(5));

  console.log("Numbers squared:", squares);
})();
```
