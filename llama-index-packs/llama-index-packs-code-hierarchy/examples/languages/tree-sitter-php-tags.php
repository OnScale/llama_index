<?php
// PHP Example showcasing various language structures

// Function definition
function calculateArea($radius) {
    return pi() * $radius * $radius;
}

// Interface definition
interface Shape {
    public function getArea();
}

// Class definition
class Circle implements Shape {
    public $radius;

    // Constructor
    public function __construct($radius) {
        $this->radius = $radius;
    }

    // Implementing the getArea method from Shape interface
    public function getArea() {
        return pi() * $this->radius * $this->radius;
    }

    // Static method
    public static function calculateAreaStatic($radius) {
        return pi() * $radius * $radius;
    }
}

// Inheritance
class Cylinder extends Circle {
    public $height;

    // Constructor
    public function __construct($radius, $height) {
        parent::__construct($radius);
        $this->height = $height;
    }

    // Overriding method
    public function getArea() {
        // Surface area of the cylinder
        $baseArea = parent::getArea();
        $circumference = 2 * pi() * $this->radius;
        return 2 * $baseArea + $circumference * $this->height;
    }

    // New method specific to Cylinder
    public function getVolume() {
        $baseArea = parent::getArea();
        return $baseArea * $this->height;
    }
}

// Using traits
trait Logger {
    public function log($message) {
        echo "Logging message: $message";
    }
}

class FileLogger {
    use Logger;
}

// Main script
$circle = new Circle(5);
echo "Circle area: " . $circle->getArea() . "\n";

$cylinder = new Cylinder(5, 10);
echo "Cylinder area: " . $cylinder->getArea() . "\n";
echo "Cylinder volume: " . $cylinder->getVolume() . "\n";

// Static method call
echo "Static Circle area: " . Circle::calculateAreaStatic(5) . "\n";

$fileLogger = new FileLogger();
$fileLogger->log("This is a log message.");
?>
