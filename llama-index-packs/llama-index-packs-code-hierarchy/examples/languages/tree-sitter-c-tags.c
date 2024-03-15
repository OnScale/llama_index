// C Example showcasing various language structures

#include <stdio.h>
#include <math.h>

// Function definition
double calculateArea(double radius) {
    return M_PI * radius * radius;
}

// Struct definition
typedef struct {
    double radius;
} Circle;

// Function associated with Circle
double circleArea(Circle c) {
    return M_PI * c.radius * c.radius;
}

// Struct definition for a Cylinder, demonstrating composition
typedef struct {
    Circle base;
    double height;
} Cylinder;

// Function associated with Cylinder
double cylinderVolume(Cylinder cy) {
    return circleArea(cy.base) * cy.height;
}

// Main function
int main() {
    Circle circle = {5.0};
    printf("Circle area: %f\n", circleArea(circle));

    Cylinder cylinder = {{5.0}, 10.0};
    printf("Cylinder volume: %f\n", cylinderVolume(cylinder));

    return 0;
}
