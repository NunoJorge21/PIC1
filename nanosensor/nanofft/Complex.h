#ifndef COMPLEX_H
#define COMPLEX_H

class Complex {
  private:
    double real;
    double imag;

  public:
    Complex(double real, double imag) : real(real), imag(imag) {}

    double getReal() const {
        return real;
    }

    double getImag() const {
        return imag;
    }

    Complex operator+(const Complex& other) const {
        return Complex(real + other.real, imag + other.imag);
    }

    Complex operator-(const Complex& other) const {
        return Complex(real - other.real, imag - other.imag);
    }

    Complex operator*(const Complex& other) const {
        return Complex(real * other.real - imag * other.imag,
                       real * other.imag + imag * other.real);
    }
};

#endif