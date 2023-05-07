import os
import sys

import numpy as np 
import pandas as pd
import pickle


from src.exception import CustomException

def save_object(file_path, obj):
    try:
        pass

    except Exception as e:
        raise CustomException(e, sys)
    
def evaluate_models(X_train, y_train,X_test,y_test,models,param):
    try:
        pass

    except Exception as e:
        raise CustomException(e, sys)
    
def load_object(file_path):
    try:
        pass

    except Exception as e:
        raise CustomException(e, sys)
