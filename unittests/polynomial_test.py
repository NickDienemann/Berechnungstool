"""
This file contains the unit tests for the Polynomial class 
"""

#resolve the BASEPATH
import re
import pathlib

from numpy.lib.polynomial import poly
BASE_PATH=pathlib.Path("".join(re.split('(point_interpolation)', str(pathlib.Path(__file__).resolve()))[:-1])) 

#imports 
import unittest
import numpy as np

import sys
sys.path.append(str(BASE_PATH.joinpath("modules")))
from polynomial import Polynomial,NoCoefficientsError
#globals


class PolynomialTestCase(unittest.TestCase):
    """
    test case for Polynomial class
    """

    def setUp(self):
        """
        task: create an instance of the Polynomial class  \n
        parameters:\n
        return value:
        """

        self.polynomial_instance= Polynomial(10)

    def test_set_coefficients(self):
        """
        task: test the set_coefficients method \n
        parameters:\n
        return value:
        """

        polynomial_instance= Polynomial(10)

        #make sure an assertion error is raised if the coefficients passed are not of fitting lenght        
        self.assertRaises(AssertionError,polynomial_instance.set_coefficients,[1,2])

        #make sure no error is raised it the number of coefficients fits the polynomial degree
        try:
            polynomial_instance.set_coefficients([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.10,0.11])
        except:
            raise AssertionError("test_set-coefficients failed, when testing fitting number of coefficents")

    def test_get_coefficients(self):
        """
        task: test the get_coefficients method \n
        parameters:\n
        return value:
        """

        polynomial_instance= Polynomial(10)

        #make sure an error is raised when there are no coefficients configured
        self.assertRaises(NoCoefficientsError,polynomial_instance.get_coefficients)

        polynomial_instance.set_coefficients([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.10,0.11])
        
        #make sure the coefficents returned are fitting
        self.assertEqual(polynomial_instance.get_coefficients(),[(10,0.1),(9,0.2),(8,0.3),(7,0.4),(6,0.5),(5,0.6),(4,0.7),(3,0.8),(2,0.9),(1,0.10),(0,0.11)])

        #make sure the coefficents are rounded properly
        self.assertEqual(polynomial_instance.get_coefficients(round_to_nth_decimalplace=1),[(10,0.1),(9,0.2),(8,0.3),(7,0.4),(6,0.5),(5,0.6),(4,0.7),(3,0.8),(2,0.9),(1,0.1),(0,0.1)]) 

    def test_evaluate(self):
        """
        task: test the evaluate method of the Polynomial \n
        parameters:\n
        return value:
        """

        polynomial_instance= Polynomial(10)
        #make sure that the no coefficients exception is raised if no coefficients were specified yet
        self.assertRaises(NoCoefficientsError,polynomial_instance.evaluate,2)

        #specify coefficients
        polynomial_instance.set_coefficients([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.10,0.11])

        #make sure an assertion error is raised if the input is not int,float,list,numpy.array
        self.assertRaises(AssertionError,polynomial_instance.evaluate,"test")

        #check if it works for int input
        self.assertEqual(polynomial_instance.evaluate(1),4.71)

        #check it it works for list input
        self.assertEqual(polynomial_instance.evaluate([1,1]),[4.71,4.71])

        #check if it works for numpy array input
        self.assertTrue(np.array_equal(polynomial_instance.evaluate(np.array([1,1])),np.array([4.71,4.71])))

    
    def test_fit_points(self):
        """
        task:  \n
        parameters:\n
        return value:
        """

if __name__=="__main__":
    unittest.main()