"""
This function holds a  class that serves as a Polynomial function
"""

#imports 
from collections import OrderedDict
from dataclasses import dataclass
import warnings
from scipy.optimize import curve_fit
import numpy as np

#globals

class NoCoefficientsError(Exception):
    """
    custom exception to signal if an evaluation is made on a polynomial without configured coefficients   
    """
    pass

@dataclass
class Polynomial():
    """
    serves as a polynomial function of varaible length
    f(x,n:degree)= a*pow(x,n)+b*pow(x,n-1)+...+g*pow(x,1)+h
    """

    def __init__(self,degree,coefficients=None):
        """
        task: inits the object and inits the coeficients if given \n
        parameters: degree(int(degree of polynomial)),coefficients(list(float(coefficients of polynomial starting at a))) \n
        return value:
        """

        #check that the given coefficients fit the given length if available
        if coefficients:
            assert degree+1==len(coefficients),f"length of coefficients ({len(coefficients)} does not fit degree ({degree})). len(coefficients)==degree+1 has to be True"

            #create an ordered dict from the given coefficients
            self.coefficients= OrderedDict([(degree-n,coef) for coef,n in enumerate(coefficients)])
        else:
            self.coefficients=coefficients    

        self.degree=degree

        #this function is used as an argument for the curve_fit method, it calculates f(x,n:degree)= a*pow(x,n)+b*pow(x,n-1)+...+g*pow(x,1)+h for a variable degree
        self.curve_func= lambda x,*args: sum([arg*pow(x,(self.degree-n)) for n,arg in enumerate(args)])

    def get_coefficients(self,round_to_nth_decimalplace=-1):
        """
        task: return the coefficients together with their degrees as degree,coef tuples starting with (degree,a),(degree-1,b) etc. \n
        parameters:round_to_nth_decimalplace(int(number of decimalplaces to round the coefficients to, default is -1 which means no rounding is done))\n
        return value: list(tuple(int(degree),float(coefficient)))
        """

        if self.coefficients:
            degree_coef_list=[]
            for degree,coef in self.coefficients.items():
                if round_to_nth_decimalplace>-1:
                    coef=round(coef,round_to_nth_decimalplace)
                degree_coef_list.append((degree,coef))
            
            return degree_coef_list

        else:
            raise NoCoefficientsError("There are no coefficients set for this Polynomial. Consider setting them explicitly with set_coefficients or using fit to derive them from a list of points")
        


    def set_coefficients(self,coefficients):
        """
        task: set the coefficients field of the class \n
        parameters: coefficients(list(float(coefficients of polynomial starting at a))) \n
        retrun value:
        """

        #make sure the number of coefficients fits the degree of the polynomial
        assert self.degree+1==len(coefficients),f"length of coefficients ({len(coefficients)}) does not fit degree ({self.degree}). len(coefficients)==degree+1 has to be True"

        #create an ordered dict from the given coefficients
        self.coefficients= OrderedDict([(self.degree-n,coef) for n,coef in enumerate(coefficients)])


    def fit_points(self,x,y):
        """
        task: use the given points (x and y pairs) to fit the polynomial to them and set the  \n
        parameters:x(np.array),y(np.array)\n
        return value estimated_covariants
        """

        #make sure the length fits
        assert len(x)==len(y),f"length of x values has to match lenght of y values, but got x({len(x)}) and y({len(y)})"

        #make sure the number of points is enough for the degree of polynomial
        assert len(x)>self.degree, f"The degree of the Polynomial+1 ({self.degree+1}) must not exceed the number of data points({len(x)})"

        coefficients,estimated_covariance= curve_fit(self.curve_func,x,y,p0=np.array([0 for _ in range(self.degree+1)])) #p0 is needed for curve fit to be able to determine the number of optimizable parameters

        self.set_coefficients(coefficients)

        return estimated_covariance

    def evaluate(self,x):
        """
        task:  \n
        parameters:\n
        return value:
        """

        assert type(x) in [int,float,list,np.ndarray],f"input has to be of type int,list or np.array, got {type(x)}"

        eval_func= lambda i: self.curve_func(i,*[coef for n,coef in self.coefficients.items()])

        if self.coefficients:
            if type(x) in [int,float]:
                return eval_func(x)
            elif type(x)==list:
                return [eval_func(i) for i in x]
            elif type(x)==np.ndarray:
                return np.array([eval_func(i) for i in x])

        #if there are no coefficients set 
        else:
            raise NoCoefficientsError("There are no coefficients set for this Polynomial. Consider setting them explicitly with set_coefficients or using fit to derive them from a list of points")

if __name__=="__main__":

    p=Polynomial(10)
    x=np.arange(0,12,1)
    y=[pow(i,2) for i in x]
    p.fit_points(x,y)
    for degree,coef in p.get_coefficients(round_to_nth_decimalplace=0):
        print(f"{degree} ______________ {coef}")