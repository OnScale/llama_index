// Java Example showcasing various language structures

import java.util.ArrayList;
import java.util.List;

// Class definition
public class Circle {
    private double radius;

    // Constructor
    public Circle(double radius) {
        this.radius = radius;
    }

    // Method
    public double getArea() {
        return Math.PI * radius * radius;
    }

    // Static method
    public static double calculateArea(double radius) {
        return Math.PI * radius * radius;
    }
}

// Interface definition
interface Shape {
    double getArea();
}

// Inheritance & implementing an interface
class Cylinder extends Circle implements Shape {
    private double height;

    // Constructor
    public Cylinder(double radius, double height) {
        super(radius); // Calling the superclass constructor
        this.height = height;
    }

    // Overriding method
    @Override
    public double getArea() {
        // Surface area of the cylinder
        return 2 * Math.PI * getRadius() * height + 2 * super.getArea();
    }

    // New method
    public double getVolume() {
        return super.getArea() * height;
    }
}

// Enum example
enum Day {
    MONDAY,
    TUESDAY,
    WEDNESDAY,
    THURSDAY,
    FRIDAY,
    SATURDAY,
    SUNDAY;
}

// Main class
public class Main {
    public static void main(String[] args) {
        Circle circle = new Circle(5);
        System.out.println("Circle area: " + circle.getArea());

        Cylinder cylinder = new Cylinder(5, 10);
        System.out.println("Cylinder area: " + cylinder.getArea());
        System.out.println("Cylinder volume: " + cylinder.getVolume());

        // Using enum
        Day day = Day.MONDAY;
        System.out.println("Day: " + day);

        // Using generics
        List<String> list = new ArrayList<>();
        list.add("Hello");
        list.add("Java");
        for (String s : list) {
            System.out.println(s);
        }
    }
}
