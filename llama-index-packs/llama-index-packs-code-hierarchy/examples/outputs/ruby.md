## ad37f65b-b2a8-48c6-be9b-449c741c74b4

```ruby
# Ruby Example showcasing various language structures

# Module definition
module MathHelpers
  PI = 3.14159

  def self.calculate_area(radius)
    PI * radius ** 2
  end
end

# Class definition
class Circle
  # Accessor methods
  attr_accessor :radius

  # Constructor method
  def initialize(radius)
    @radius = radius
  end

  # Instance method
  def area
    MathHelpers::PI * @radius ** 2
  end

  # Class method
  def self.from_diameter(diameter)
    Circle.new(diameter / 2)
  end
end

# Inheritance example
class Cylinder < Circle
  attr_accessor :height

  def initialize(radius, height)
    super(radius) # Calls the parent class's initialize method
    @height = height
  end

  # Overriding method
  def area
    2 * super + circumference * @height # Calls the parent class's area method
  end

  # New method
  def volume
    super * @height
  end

  def circumference
    2 * MathHelpers::PI * @radius
  end
end

# Using a Proc
square = Proc.new { |x| x ** 2 }

# Lambda example
adder = ->(a, b) { a + b }

# Enumerable and blocks
def fibonacci_sequence(n)
  seq = [0, 1]
  (2...n).each { |i| seq << seq[i - 1] + seq[i - 2] }
  seq
end

# Mixin and Modules
module Debuggable
  def debug
    puts "Debugging #{self.class.name}..."
  end
end

class DebugCircle < Circle
  include Debuggable
end

# Main block to execute some examples
if __FILE__ == $0
  circle = Circle.new(5)
  puts "Circle area: #{circle.area}"
  cylinder = Cylinder.new(5, 10)
  puts "Cylinder area: #{cylinder.area}"
  puts "Cylinder volume: #{cylinder.volume}"

  fib_seq = fibonacci_sequence(10)
  puts "Fibonacci sequence (first 10 numbers): #{fib_seq.join(', ')}"

  sum_result = adder.call(5, 3)
  puts "Sum of 5 and 3: #{sum_result}"
end

```
