#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''

import sys,os
from sklearn import feature_selection, cross_validation, ensemble, metrics, svm, naive_bayes
import numpy as np
from scipy.stats import chi2
from makeMatrix import MatrixFactory
from myDb import ExtendedDB

class Main(object):
    signifikanzNiveau = 0.7

    def __init__(self):
        self.db = ExtendedDB(commitOnClose=False)
        self.X,self.y,self.X_eval,self.ids_eval,self.columns = MatrixFactory().loadFromFile()
        #clf=ensemble.RandomForestClassifier(n_estimators=66)
        #clf=svm.SVC(kernel="linear",gamma=0.01, C=250, class_weight='balanced')
        clf=naive_bayes.MultinomialNB(alpha=0.01)
        self.clf = clf
        
    def classify(self):
        print("classifying")
        self.clf.fit(self.X,self.y)
        y_pred = self.clf.predict(self.X_eval)
        self.db.query("DELETE FROM predictions")
        for i, cls in zip(self.ids_eval, y_pred):
            self.db.save("predictions",id=i,cls=int(cls))
        self.db.commit()
        print("done.")
        
    def crossvali(self):
        print("crossvalidation")
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(
                    self.X, self.y, test_size=0.1, random_state=8198987, stratify=self.y)
        self.clf.fit(X_train,y_train)
        y_pred = self.clf.predict(X_test)
        print(metrics.confusion_matrix(y_test, y_pred))
        print(metrics.classification_report(y_test, y_pred, target_names=sorted(set([str(x) for x in (y_test.tolist()+y_pred.tolist())]))))

    def chi2(self):
                df = len(self.columns) # freiheitsgrad
                #krit = chi2.ppf(0.95, df)
                krit = chi2.ppf(self.signifikanzNiveau, df)
                print("Kritischer Wert chi² = %0.3f"%krit)        

                limit = 50
                skb = feature_selection.SelectKBest(feature_selection.chi2, k=limit)
                skb.fit(self.X, self.y)
                a=[(idx_,score) for idx_,score in enumerate(skb.scores_) if not np.isnan(score)]
                a=sorted(a,key=lambda x:x[1], reverse=True)
                most=[(self.columns[idx_],score) for idx_,score in a[:limit]]
                msg = u"\n\t".join([u"%s (%0.3f)"%(name,score) for name,score in most])
                sys.stderr.write((u"%s\n"%msg).encode("utf-8",errors="strict"))

    
Classifier = Main
    
if __name__ == "__main__":
    Main()()

