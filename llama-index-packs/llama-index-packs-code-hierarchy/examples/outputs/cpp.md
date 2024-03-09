## a9c74d38-fdf0-42a5-bac2-237c724bda5b

```cpp
// C++ Example showcasing various language structures

#include <iostream>
#include <cmath>
using namespace std;

// Function definition
double calculateArea(double radius) {
    return M_PI * radius * radius;
}

// Class definition
class Circle {
public:
    double radius;
    // Constructor
    Circle(double r) : radius(r) {}
    // Method
    double area() {
        return M_PI * radius * radius;
    }
};

// Inheritance
class Cylinder : public Circle {
public:
    double height;
    // Constructor
    Cylinder(double r, double h) : Circle(r), height(h) {}
    // Overriding method
    double area() {
        // Surface area of the cylinder
        return 2 * M_PI * radius * height + 2 * Circle::area();
    }
    // New method
    double volume() {
        return Circle::area() * height;
    }
};

// Template function
template <typename T>
T max(T a, T b) {
    return (a > b) ? a : b;
}

// Main function
int main() {
    Circle circle(5);
    cout << "Circle area: " << circle.area() << endl;

    Cylinder cylinder(5, 10);
    cout << "Cylinder area: " << cylinder.area() << endl;
    cout << "Cylinder volume: " << cylinder.volume() << endl;

    cout << "Max of 10 and 20: " << max(10, 20) << endl;
    cout << "Max of 15.5 and 8.2: " << max(15.5, 8.2) << endl;

    return 0;
}

```
