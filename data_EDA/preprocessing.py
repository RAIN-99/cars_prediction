import pandas as pd 
import numpy as np 

full_data=pd.read_csv("../data/data_cars.csv")
# full_data['mileage']=full_data['mileage'].str.replace(' ','')
# full_data['mileage']= full_data['mileage'].astype(float)
# print(full_data.select_dtypes(object))
# print(full_data.select_dtypes('number'))
def fill_missing_values(data):
    categorical_columns = data.select_dtypes(object).columns.tolist()
    data[categorical_columns] = data[categorical_columns].fillna("MISSING")
    

    numerical_columns = data.select_dtypes('number').columns.tolist()
    data[numerical_columns] = data[numerical_columns].fillna(-999)
    return data
full_data = fill_missing_values(full_data)

full_data.to_csv("../data/data_cars.csv",index=False)