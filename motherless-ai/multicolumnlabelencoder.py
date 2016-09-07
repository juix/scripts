"""
Based on http://stackoverflow.com/questions/24458645/label-encoding-across-multiple-columns-in-scikit-learn; 01.06.2016.

"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline

class MultiColumnLabelEncoder:
    def __init__(self,columns = None):
        self.columns = columns # array of column names to encode
        self.labels = dict()

    def fit(self,X,y=None):
        return self # not relevant here

    def transform(self,X):
        '''
        Transforms columns of X specified in self.columns using
        LabelEncoder(). If no columns specified, transforms all
        columns in X.
        '''
        output = X.copy()
        if self.columns is not None:
            columns = set(output.keys()).intersection(self.columns)
            for colname in columns:
                #if not colname in output: continue
                enc = LabelEncoder()
                output[colname] = enc.fit_transform(output[colname])
                self.labels[colname] = enc
        else:
            for colname,col in output.iteritems():
                enc = LabelEncoder()
                output[colname] = enc.fit_transform(col)
                self.labels[colname] = enc
        return output

    def fit_transform(self,X,y=None):
        return self.fit(X,y).transform(X)
