"""
main file for the web app
"""

#resolve the BASEPATH
import re
import pathlib

BASE_PATH=pathlib.Path("".join(re.split('(bachelorarbeit_tom)', str(pathlib.Path(__file__).resolve()))[:-1])) 


#imports
from flask import Flask,render_template, request, url_for, flash, redirect          # import flask
import sqlite3
from werkzeug.exceptions import abort
import json
import base64
import numpy as np
import matplotlib.pyplot as plt
import re

import sys
sys.path.append(str(BASE_PATH.joinpath("modules")))
from polynomial import Polynomial
from polynomial_storage import Polynomial_storage, Key_element, Storage_manager 


#globals
STORAGE_PATH=BASE_PATH.joinpath("web_app","permanent_storage")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dieser wundervolle key beschuetzt meine Daten'
app.config['EXPLAIN_TEMPLATE_LOADING']= True

@app.route('/', methods=('GET','POST'))
def start_page():
    if request.method=="POST":
        if "save_button" in request.form.keys():
            storage_manager.save_storages()

        #check if a storage was set to be deleted
        button_regex=re.compile("delete_button___")
        for key in request.form.keys():
            if re.match(button_regex,key):
                storage_name=re.split(button_regex,key)[-1]
                storage_manager.delete_storage_by_name(storage_name)
               

    return render_template('start_page.html',storage_manager=storage_manager)

@app.route('/<string:storage_name>', methods=('GET','POST'))
def storage(storage_name):

    current_storage= storage_manager.get_storage_by_name(storage_name)
    storage_manager.set_current_storage(storage_name)
    current_storage_name,current_storage=storage_manager.get_current_storage()

    storage_content=enumerate(current_storage.storage.items())
    key_structure= current_storage.get_key_structure()
    return render_template('index.html',storage_content=storage_content,key_structure=key_structure,current_storage_name=current_storage_name)

@app.route('/<string:storage_name>/<string:storage_element_key>', methods=['GET','POST'])
def storage_element(storage_element_key,storage_name):

    current_storage_name,current_storage=storage_manager.get_current_storage()

    storage_element = get_storage_element(storage_element_key)
    key_structure= current_storage.get_key_structure()

    evaluation=None
    x_start,x_end=None,None
    #if its a post request, check what was entered into the form
    if request.method=="POST":
        #create evaluation of polynomial, if points given
        if "points_to_evaluate" in request.form.keys():
            points_to_evaluate=request.form['points_to_evaluate']
            points_to_evaluate=json.loads(points_to_evaluate)
            evaluation=storage_element.polynomial.evaluate(points_to_evaluate)

        #check if the form holds a new value for x_start or x_end
        if "x_start" in request.form.keys():
            try:
                x_start=float(request.form['x_start'])
            except ValueError:
                pass
        if "x_end" in request.form.keys():
            try:
                x_end=float(request.form['x_end']) 
            except ValueError:
                pass

    #store the plot within the plots folder to make it available within the current_plot directory
    dest_path=BASE_PATH.joinpath("web_app","current_plot","polynomial_plot.png")

    #create a plot for the possibly given x start and end values
    xs_dict=dict([(key,value) for key,value in {"x_start":x_start,"x_end":x_end}.items() if value is not None])
    storage_element.plot_polynomial(dest_path=dest_path,**xs_dict)

    #encode the png as base 64
    with open(dest_path,"rb") as img_file:
        encoded_image= base64.b64encode(img_file.read()).decode('utf-8')
    
    return render_template('storage_element.html', storage_element=storage_element,encoded_image=encoded_image,evaluation=evaluation,storage_element_key=string_2_storage_element_key(storage_element_key),key_structure=key_structure,current_storage_name=current_storage_name)

@app.route('/<string:storage_name>/add_storage_element', methods=('GET', 'POST'))
def add_storage_element(storage_name):

    current_storage_name,current_storage=storage_manager.get_current_storage()

    #get the structure of the polynomial
    key_structure= current_storage.get_key_structure()

    #if its a post request then use the values within the form to create a new storage_element 
    if request.method =="POST":
        key_kwargs= {}
        for pos, key_element in key_structure.items():
            
            #check if the form can be converted to float
            try:
                key_kwargs[key_element.name]=float(request.form[f'{pos}'])
                
            except:
                key_kwargs[key_element.name]=request.form[f'{pos}']

        dest_path= request.form['dest_path']
        col_feature= request.form['col_feature']
        col_target= request.form['col_target']
        polynomial_degree= int(request.form['polynomial_degree'])

        filter_func= None
        if request.form['filter_column']!="":
            filter_column= request.form['filter_column']
            filter_value= request.form['filter_value']
            
            #try to convert the filter_value to numeric if possible
            try:
                filter_value= float(filter_value)
            except ValueError:
                pass

            filter_func= lambda df: df.loc[df[filter_column]==filter_value] 
            

        #store the object
        #filter_func= lambda df: df.loc[df["Schwenkwangenanstellung"]==key_kwargs["schwenkwangenanstellung"]]
        current_storage.store_polynomial_from_excel(dest_path,col_feature,col_target,polynomial_degree,**key_kwargs,filter_func=filter_func)


    return render_template("add_storage_element.html", key_structure=key_structure,current_storage_name=current_storage_name)

@app.route('/interpolate_storage_element', methods=('GET', 'POST'))
def interpolate_storage_element():

    current_storage_name,current_storage=storage_manager.get_current_storage()

    #get the structure of the polynomial
    key_structure= current_storage.get_key_structure()

    #if its a post request then use the values within the form to create a new storage_element 
    if request.method =="POST":
        key_kwargs= {}
        for pos, key_element in key_structure.items():
            
            #check if the form can be converted to float
            try:
                #check if the form contains a [] if so, try to convert it into a list by using json
                if "[" in request.form[f'{pos}']:
                    key_kwargs[key_element.name]=json.loads(request.form[f'{pos}'])
                else:
                    key_kwargs[key_element.name]=float(request.form[f'{pos}'])
                
            except:
                key_kwargs[key_element.name]=request.form[f'{pos}']

        interpol_points=json.loads(request.form["interpol_points"])
        target_key_arg=float(request.form["target_key_arg"])

        current_storage.interpolate_polynomial(interpol_points,target_key_arg,**key_kwargs)

    return render_template("interpolate_storage_element.html", key_structure=key_structure)

@app.route('/add_storage', methods=('GET', 'POST'))
def add_storage():
    
    current_storage_name,current_storage=storage_manager.get_current_storage()

    if request.method=="POST":
       
        #get the desired key_structure and storage_name
        key_elements=string_2_key_elements(request.form["key_elements"])
        storage_name= request.form["storage_name"]

        polynomial_storage=Polynomial_storage(key_elements)

        storage_manager.add_storage(storage_name,polynomial_storage)

    return render_template("add_storage.html")

def string_2_storage_element_key(storage_element_key):
    storage_element_key=storage_element_key.replace("\'","\"")
    return json.loads(storage_element_key)

def string_2_key_elements(key_elements):

    key_structure=key_elements.replace("\'","\"")
    key_elements=json.loads(key_elements)
    key_element_instances=[]
    for key_element in key_elements:
        key_element_instances.append(Key_element(*key_element) )

    return key_element_instances

def get_storage_element(storage_element_key):

    current_storage_name,current_storage=storage_manager.get_current_storage()

    storage_element_key =string_2_storage_element_key(storage_element_key)
    storage_element_key= dict(zip(map(lambda key_el: key_el.name,current_storage.key_structure.values()),storage_element_key))
    storage_element= current_storage.get_object(**storage_element_key)
    if storage_element is None:
        abort(404)
    return storage_element

if __name__=="__main__":

    #----create the storage manager----
    storage_manager=Storage_manager(STORAGE_PATH)#pathlib.Path(r"C:\Users\nick\Code\MachineLearning_Projects\opencv_pytorch_projects\math_tools\point_interpolation\permanent_storage\storages"))
    storage_manager.load_storages()

#-------------------------------------------storage ------------------------------------------------------
    #create a storage 
    #key_elements=[Key_element("schwenkwangenanstellung",0,"mm"),Key_element("blechdicke",1,"mm"),Key_element("target_variable",2,"any")]
    #storage= Polynomial_storage(key_elements=key_elements)

    #fill the storage
    #for schwenkwangenanstellung in [1,2,3,5,7,10]: 
        #filter_func= lambda df: df.loc[df["Schwenkwangenanstellung"]==schwenkwangenanstellung]
        #storage.store_polynomial_from_excel(r"C:\Users\nick\Code\MachineLearning_Projects\opencv_pytorch_projects\math_tools\point_interpolation\data\Werkstoff_DC04.xlsx","Rotationswinkel_schwenkwange","alpha_1",4,schwenkwangenanstellung=schwenkwangenanstellung,blechdicke=1.5,target_variable="alpha_1",filter_func=filter_func)

    #print(storage.get_object(schwenkwangenanstellung=1,blechdicke=1.5,target_variable="alpha_1"))
    #print(storage.get_object_range(schwenkwangenanstellung=[1,2,3,5,7,10],blechdicke=1.5,target_variable="alpha_1"))
#-------------------------------------------storage ------------------------------------------------------    


    try:
        app.run(debug=True)
    finally:
        #if there was a current storage already, store that back into the storage manager cuz the global reference detaches it
        #if current_storage and current_storage_name:
        #    storage_manager.storage_cache[current_storage_name]=current_storage

        #storage_manager.save_storages() #save all changes made
        #print("succesfully saved storages")
        pass
