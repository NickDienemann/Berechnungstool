"""
This file serves as a storage for different polynomials. Querry parameters are:
- Schwenkwangenanstellung
- Blechdicke
- Werkstoff
- Rotationsgrad

für jeden der daraus ergebenden keys können len(target_parameter choices) polynoimals hinterlegt werden, die dann über den target_parameter aus (alpha_1,alpha_2,biegeradius_1,biegeradius_2) ausgewählt werden könnnen

das wäre der storage teil. es gibt aber auch den interpolierenden teil des storage, wobei ein unbekannter eintrag aus den bekannten heraus interpoliert werden kann
"""

#resolve the BASEPATH
import re
import pathlib

BASE_PATH=pathlib.Path("".join(re.split('(bachelorarbeit_tom)', str(pathlib.Path(__file__).resolve()))[:-1])) 

#imports 
from dataclasses import dataclass
from polynomial import Polynomial
import numpy as np
import pandas as pd
import warnings
import dill
import matplotlib.pyplot as plt
import os

import sys
sys.path.append(str(BASE_PATH.joinpath("modules")))
from error_history import Error_history

#globals
STORAGE_PATH= BASE_PATH.joinpath("permanent_storage","storage.obj")
INTERPOLATED_POLYNOMIAL_DEGREE=4
STORE_INTERPOLATION_POINTS=True


class Base_storage():
    """
    class that is a base class for the storage
    """

    def __init__(self,key_elements):
        """
        task: inits the object and desribes how many parameters are used to querry a polynomial\n
        parameters:key_elements(list(Key_element instances))\n
        return value:
        """

        self.storage={}
        self.key_structure=dict(map(lambda key_el: (key_el.position,key_el),key_elements))

    def store_object(self,obj,**key_kwargs):
        """
        task: store the given object at the key specified by key_args \n
        parameters: obj(Any), *key_kwargs(keywordarguments used for key generation) \n
        return value:
        """

        key= self.__kwargs_to_key(**key_kwargs)

        self.storage[key]=obj

    def get_key_structure(self):
        """
        task: return the key structure of the storage \n
        parameters:\n
        return value: dict(key structure)
        """

        return self.key_structure

    def get_object(self,**key_kwargs):
        """
        task: return the object specified by the given key arguments  \n
        parameters: *key_args(arguments used for key generation) \n
        return value:
        """

        key= self.__kwargs_to_key(**key_kwargs)
        try:
            return self.storage[key]
        except KeyError:
            raise KeyError(f"The given key {key} could not be found in the storage ")

    def get_object_range(self,**key_kwargs):
        """
        task: return the object specified by the given key arguments  \n
        parameters: **key_kwargs(keywordarguments used for key generation) \n
        return value:
        """

        #get the keyword argument that is expressed by a list and then genrate all corresponding keys
        kwarg_copy= key_kwargs.copy()
        keys=[] 
        for key,kwarg in key_kwargs.items():
            #fetch each key from that list
            if type(kwarg)==list:
                for el in kwarg:
                    kwarg_copy[key]=el
                    keys.append(self.__kwargs_to_key(**kwarg_copy))

        objects=[]
        for key in keys:
            try:
                objects.append(self.storage[key])
            except KeyError:
                raise KeyError(f"The given key {key} could not be found in the storage ")

        return objects

    def remove_object(self,**key_kwargs):
        """
        task: remove the object specified by the given key arguments\n
        parameters: **key_kwargs(keywordarguments used for key generation) \n
        return value:
        """

        key= self.__kwargs_to_key(**key_kwargs)
        try:
            self.storage.pop(key)
        except KeyError:
            raise KeyError(f"The given key {key} could not be found in the storage ")

    def __kwargs_to_key(self,**kwargs):
        """
        task: take an arbitrary number of arguments and transform them into one key of type string \n
        parameters: *args(arbitrary number of arguments used for key generation) \n
        return value: tuple(key generated from *args)
        """

        #check if the length of arguments fits the n_querry_parameters
        assert len(kwargs)==len(self.key_structure), f"The number of arguments passed to create the key({len(kwargs)}) have to fit the number of querry parameters specified({len(self.key_structure)})"

        #check if the given arguments fullfill the key elements name
        for pos,kwarg in enumerate(kwargs.items()):
            assert self.key_structure[pos].name== kwarg[0], f"The key at position {pos} does not fit the required name for that position. Got {kwarg[0]} but needed {self.key_structure[pos].name}"

        key=None
        try:
            key=tuple(kwargs.values())            
        except TypeError:
            raise TypeError("the arguments for key generation are invalid")

        return key

    def save_storage(self,path_to_save_to):
        """
        task: pickle the self.storage field to the given path \n
        parameters: path_to_save_to(str) \n
        return value:
        """

        with open(path_to_save_to,"wb") as f:
            dill.dump(self.storage,f)
            f.close()

    def load_storage(self,path_to_load_from):
        """
        task: unpickle the storage at given path and set the self.storage field to it \n
        parameters: path_to_load_from(str) \n
        return value:
        """

        with open(path_to_load_from,"rb") as f:
            self.storage=dill.load(f)
            f.close()



class Polynomial_storage(Base_storage):
    """
    this class serves as an enhancement to the original Polynomial_storage class by creating a stricter key generation
    """

    def __init__(self,key_elements,fitting_error_func=lambda y_pred,y_hat: sum(np.square(y_pred-y_hat))/len(y_pred)):
        """
        task: create the object and set its key structure \n
        parameters: n_querry_parameters(int(number of parameters of query)) \n
        return value:
        """

        super().__init__(key_elements)
        self.fitting_error_func=fitting_error_func

    def store_polynomial_from_excel(self,path_to_excel,feature_column,target_column,polynomial_degree,filter_func=None,**key_kwargs):
        """
        task: store the polynomial derived from the data within the csv file  \n
        parameters: path_to_excel(string(absolute path to excel file)),feature_column(columnname of feature),target_column(columnname of target),*key_args,filter_func(callable, if passed this func is called on the df derived from excel file) \n
        return value:
        """

        #read csv
        df= pd.read_excel(path_to_excel)

        #apply filter if given
        if filter_func:
            df=filter_func(df)

        #create x and y variables
        x,y=np.array(df[feature_column]),np.array(df[target_column])

        #create a warning if the data contains nan values
        if any(np.isnan(x)) or any(np.isnan(y)):     
            warnings.warn(f"The given data contains NaN values. This might lead to errors!")

        #create the storage element
        el=Polynomial_storage_element(polynomial_degree,x,y,fitting_error_func=self.fitting_error_func)

        #store the element
        self.store_object(el,**key_kwargs)

    def evaluate_polynomial(self,x,**key_kwargs):
        """
        task: evaluate the polynomial specified by the key args at value/values x \n
        parameters: x(float, list(float) or numpy.array of values to evaluate), *args(arbitrary number of arguments used for key generation) \n
        return value: float, list(float) or numpy.array, corresponding to input format
        """ 

        polynomial=self.get_object(**key_kwargs)
        return polynomial.polynomial.evaluate(x)

    def interpolate_polynomial(self,x,target_key_arg,**key_kwargs):
        """
        task: interpolate a polynomial, by using the polynomials specified by key_args+ iterable_key_arg evaluated at x and then interpolate the values at target_key_arg \n
        parameters: x(float, list(float) or numpy.array of values to evaluate),target_key_arg(value to interpolate at), iterable_key_arg(list(list of values that will be used as key args to find paretn polynomials)) \n
        return value:
        """
    
        #get the polynomials that will be used for interpolation
        parent_polynomials=self.get_object_range(**key_kwargs)

        #get the key_arg that is a range/list
        iterable_key,iterable_key_arg,iterable_key_arg_pos= [(kwarg,value,pos) for pos,(kwarg,value) in enumerate(key_kwargs.items()) if type(value)==list][0]

        #evaluate each of those polynomials at x
        parent_y_values={}
        for arg,parent_poly in zip(iterable_key_arg,parent_polynomials):
            parent_y_values[arg]=parent_poly.polynomial.evaluate(x)

        #interpolate a y value for each x value by using the parent y_values 
        interpolated_y_values=[]
        interpolated_key_arg_polynomials=[]
        for index,x_val in enumerate(x):
            
            #iterate over the y values of the parents and 
            parent_key_args=np.array(list(parent_y_values.keys()))
            parent_y_vals_for_current_x=np.array([y_vals[index] for y_vals in parent_y_values.values()])

            #interpolate a polynomial on that data 
            interpolated_key_arg_polynomial=Polynomial_storage_element(INTERPOLATED_POLYNOMIAL_DEGREE,parent_key_args,parent_y_vals_for_current_x)            
            interpolated_key_arg_polynomials.append(interpolated_key_arg_polynomial)
            interpolated_key_arg_polynomial.forge_error_history_from_parents(parent_polynomials)#forge the history of the parent polynomials

            #evaluate the interpolated polynomial at the given x values
            interpolated_y_values.append(interpolated_key_arg_polynomial.polynomial.evaluate(target_key_arg))
                

        #interpolate a final polynomial on the interpolated y values and store that polynomial at key_args+target_key_arg
        final_polynomial=Polynomial_storage_element(INTERPOLATED_POLYNOMIAL_DEGREE,np.array(x),np.array(interpolated_y_values))
        final_polynomial.forge_error_history_from_parents(interpolated_key_arg_polynomials)#forge the parent error histories

        #key_kwargs.insert(iterable_key_arg_pos,target_key_arg)
        key_kwargs[iterable_key]=target_key_arg
        self.store_object(final_polynomial,**key_kwargs)




@dataclass
class Polynomial_storage_element():
    """
    this class serves as an element that can be stored in the Polynomial_storage 
    """

    polynomial: Polynomial
    error_history: Error_history      

    def __init__(self,polynomial_degree,x,y,fitting_error_func=lambda y_pred,y_hat: sum(np.square(y_pred-y_hat))/len(y_pred)):
        """
        task: inits the object by interpolating the given points with an order-n polynomial and storing the fitting error \n
        parameters: polynomial_degree(int(degree of the polynomial to fit)),x(np.array),y(np.array),fitting_error_func(callable(takes y_pred and y_hat as input and calcs error)) \n
        return value:
        """

        self.polynomial= Polynomial(polynomial_degree)                          #create polynomial of desired degree
        self.polynomial.fit_points(x,y)                                         #fit the given points
        self.error_history= Error_history(fitting_error_func(self.polynomial.evaluate(x),y))   #calculate the fitting error and save that in the error history
        if STORE_INTERPOLATION_POINTS:
            self.x=x
            self.y=y

    def forge_error_history_from_parents(self,parent_elements):
        """
        task: forge the given parent histories to the current error tree \n
        parameters: parent_elements(list(Polynomial_storage_element instances)) \n
        return value:
        """

        self.error_history.forge_from_parents([p_e.error_history for p_e in parent_elements])

    def plot_polynomial(self,dest_path=None,x_start=0,x_end=120):
        """
        task: plots the polynomial together with the points it was interpolated from, if available \n
        parameters: dest_path(Path(if given this will be the path that the plot will be saved in)) \n
        return value:
        """

        #create an x to 
        x=np.arange(x_start,x_end,0.1)

        #create a plot and plot the function
        fig= plt.figure()
        plt.plot(x,self.polynomial.evaluate(x),"blue")

        #if available, print the point that were used to interpolate the given polynomial
        if (self.x is not None) and (self.y is not None):
            plt.plot(self.x,self.y,"o",color="red")

        #set x lim to x_start and x_end
        plt.xlim(x_start,x_end)

        if not dest_path:
            plt.show()
        else:
            fig.savefig(dest_path)

@dataclass
class Key_element():
    """
    this class serves as a definition for key elements, which are the components used for key generation in the proposed storages
    """

    name: str
    position: int
    unit: str 

class Storage_manager():
    """
    This class will be used as a wrapper class for storages. It will hold functionality to keep track of multiple storage instances
    """

    def __init__(self,storage_path):
        """
        task: inits the object and set the storage path \n
        parameters: storage_path(Path) \n
        return value:
        """

        self.storage_path=storage_path
        self.storage_cache={}
        self.current_name_and_storage=(None,None)

    def save_storages(self):
        """
        task: pickle all storage instances within the storage_cache field to the given path \n
        parameters: \n
        return value:
        """

        for storage_name,storage_instance in self.storage_cache.items():
            with open(self.storage_path.joinpath(storage_name+".obj"),"wb") as f:
                dill.dump(storage_instance,f)
                f.close()

    def load_storages(self):
        """
        task: unpickle the storages at given path and load them into the cache \n
        parameters:\n
        return value:
        """

        for file_name in os.listdir(self.storage_path):
            with open(self.storage_path.joinpath(file_name),"rb") as f:
                shortened_file_name=file_name.split(".")[0]
                self.storage_cache[shortened_file_name]=dill.load(f)
                f.close()

    def add_storage(self,storage_name,storage_instance):
        """
        task: add the specified storage_instance to the cache \n
        parameters:\n
        return value:
        """

        self.storage_cache[storage_name]=storage_instance

    def get_cache(self):
        """
        task: return the self.storage_cache field \n
        parameters:\n
        return value: dict
        """

        return self.storage_cache

    def get_storage_by_name(self,storage_name):
        """
        task: return the storage with the specified name \n
        parameters:\n
        return value:storage instance
        """

        return self.storage_cache[storage_name]

    def set_current_storage(self,storage_name):
        """
        task: sets the storage stored at that name as the current storage\n
        parameters:storage_name(String)\n
        return value:
        """

        self.current_name_and_storage= (storage_name,self.get_storage_by_name(storage_name))

    def get_current_storage(self):
        """
        task: return the current_name_and_storage field\n
        parameters:\n
        return value: tuple(String,storage instance)
        """

        return self.current_name_and_storage

    def delete_storage_by_name(self,storage_name, delete_permanently=True):
        """
        task: delte the storage with the given name \n
        parameters: storage_name(String), delete_permanently(boolean(if true the entry is also removed from the permanent storage))\n
        return value:
        """

        #remove the entry from cache
        self.storage_cache.pop(storage_name)

        #if specified, delete it from the permanent storage as well
        if delete_permanently:
            try:
                os.remove(self.storage_path.joinpath(storage_name+".obj"))
            except FileNotFoundError:
                pass

if __name__=="__main__":
    if False:
        #create a storage 
        key_elements=[Key_element("schwenkwangenanstellung",0,"mm"),Key_element("blechdicke",1,"mm"),Key_element("target_variable",2,"any")]
        storage= Polynomial_storage(key_elements=key_elements)

        #fill the storage
        for schwenkwangenanstellung in [1,2,3,5,7,10]: 
            filter_func= lambda df: df.loc[df["Schwenkwangenanstellung"]==schwenkwangenanstellung]
            storage.store_polynomial_from_excel(r"C:\Users\nick\Code\MachineLearning_Projects\opencv_pytorch_projects\math_tools\point_interpolation\data\Werkstoff_DC04.xlsx","Rotationswinkel_schwenkwange","alpha_1",4,schwenkwangenanstellung=schwenkwangenanstellung,blechdicke=1.5,target_variable="alpha_1",filter_func=filter_func)

        print(storage.get_object(schwenkwangenanstellung=1,blechdicke=1.5,target_variable="alpha_1"))
        print(storage.get_object_range(schwenkwangenanstellung=[1,2,3,5,7,10],blechdicke=1.5,target_variable="alpha_1"))

        #interpolate the polynomial for 4
        key_kwargs={'schwenkwangenanstellung': [1, 2, 3, 5, 7, 10], 'blechdicke': 1.5, 'target_variable': 'alpha_1'}
        interpol_points=[10,20,30,40,50]
        target_key_arg=4
        storage.interpolate_polynomial(interpol_points,target_key_arg,**key_kwargs)

        storage.get_object(schwenkwangenanstellung=4,blechdicke=1.5,target_variable="alpha_1").error_history.render_history()

        #store the storage
        storage_manager=Storage_manager(pathlib.Path(r"C:\Users\nick\Code\MachineLearning_Projects\opencv_pytorch_projects\math_tools\point_interpolation\permanent_storage\storages"))
        storage_manager.add_storage("storage_two",storage)
        storage_manager.save_storages()
    

    storage_manager=Storage_manager(pathlib.Path(r"C:\Users\nick\Code\MachineLearning_Projects\opencv_pytorch_projects\math_tools\point_interpolation\permanent_storage\storages"))
    print(storage_manager.get_cache())
    storage_manager.load_storages()
    #storage_manager.set_current_storage("storage_four")
    
    print(storage_manager.get_cache())
    print(id(storage_manager.get_storage_by_name("storage_four")))
    print(id(storage_manager.storage_cache["storage_four"]))