// C# Example showcasing various language structures

using System;

// Interface definition
public interface IShape {
    double GetArea();
}

// Class definition
public class Circle : IShape {
    public double Radius { get; set; }

    // Constructor
    public Circle(double radius) {
        Radius = radius;
    }

    // Method implementing the IShape interface
    public double GetArea() {
        return Math.PI * Radius * Radius;
    }

    // Static method
    public static double CalculateArea(double radius) {
        return Math.PI * radius * radius;
    }
}

// Inheritance
public class Cylinder : Circle {
    public double Height { get; set; }

    // Constructor
    public Cylinder(double radius, double height) : base(radius) {
        Height = height;
    }

    // Overriding method
    public new double GetArea() {
        // Surface area of the cylinder
        return 2 * Math.PI * Radius * Height + 2 * base.GetArea();
    }

    // New method specific to Cylinder
    public double GetVolume() {
        return base.GetArea() * Height;
    }
}

// Main class
class Program {
    static void Main(string[] args) {
        Circle circle = new Circle(5);
        Console.WriteLine("Circle area: " + circle.GetArea());

        Cylinder cylinder = new Cylinder(5, 10);
        Console.WriteLine("Cylinder area: " + cylinder.GetArea());
        Console.WriteLine("Cylinder volume: " + cylinder.GetVolume());

        // Using static method
        double area = Circle.CalculateArea(5);
        Console.WriteLine("Area from static method: " + area);
    }
}
