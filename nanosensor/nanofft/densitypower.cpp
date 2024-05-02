#import <Arduino.h>
#import <math.h>
#import "Complex.h"

//Function returns the absolute value of a given complex number
double complexAbs(const Complex& c) {
    return sqrt(c.getReal() * c.getReal() + c.getImag() * c.getImag());
}

int main(){
    //Variáveis já declaradas no arduino
    int frequency = 25000; //Sampling frequency
    int NSAMP = 10000; //Number of samples
    int sampled[NSAMP]; //Samples vector

    //Variáveis a declarar
    int NF = 5000; //Number of frequency points needed for the unilateral density power (NSAMP/2)
    Complex j(0.0, 1.0); //Initialization of imaginary unit
    Complex X[NF]; //Vector used to calculate the fourier transform with the samples obtained
    //float res = frequency/NSAMP; //Frequency resolution
    //float F[NF]; //Frequency vector
    float S[NF]; //Power density

    for(int i = 0; i < NF; i++){
        for(int k = 0; k < NSAMP; k++){
            X[i] += sampled[k]*(cos((2*M_PI*k*i)/NSAMP) - j*sin((2*M_PI*k*i)/NSAMP));
        }
        //F[j] = res*j;
        if(j == 0 || j == NF - 1) S[j] = pow(complexAbs(X[j])/NSAMP, 2);
        else S[j] = 2*pow(complexAbs(X[j])/NSAMP,2);
    }

    return 0;
}