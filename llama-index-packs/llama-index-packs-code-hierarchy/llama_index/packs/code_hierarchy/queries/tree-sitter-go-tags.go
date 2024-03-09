// Go Example showcasing various language structures

package main

import (
    "fmt"
    "math"
)

// Function definition
func calculateArea(radius float64) float64 {
    return math.Pi * radius * radius
}

// Struct definition
type Circle struct {
    Radius float64
}

// Method (function with a receiver)
func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}

// Interface definition
type Shape interface {
    Area() float64
}

// Inheritance is not directly supported in Go, but we can achieve polymorphism with interfaces
type Cylinder struct {
    Circle // Embedding (Composition)
    Height float64
}

// Method overriding
func (c Cylinder) Area() float64 {
    // Surface area of the cylinder
    baseArea := c.Circle.Area()
    circumference := 2 * math.Pi * c.Circle.Radius
    return 2*baseArea + circumference*c.Height
}

// New method specific to Cylinder
func (c Cylinder) Volume() float64 {
    baseArea := c.Circle.Area()
    return baseArea * c.Height
}

// Main function
func main() {
    circle := Circle{Radius: 5}
    fmt.Printf("Circle area: %v\n", circle.Area())

    cylinder := Cylinder{Circle{Radius: 5}, Height: 10}
    fmt.Printf("Cylinder area: %v\n", cylinder.Area())
    fmt.Printf("Cylinder volume: %v\n", cylinder.Volume())

    // Interface usage
    var shape Shape = Circle{Radius: 5}
    fmt.Printf("Shape area (Circle): %v\n", shape.Area())
    shape = Cylinder{Circle{Radius: 5}, Height: 10}
    fmt.Printf("Shape area (Cylinder): %v\n", shape.Area())
}

// Go uses structs and interfaces to achieve many of the same things as classes and inheritance in other languages.
