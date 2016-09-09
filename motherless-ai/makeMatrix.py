#!/usr/bin/env python
# -*- coding: utf-8 -*- 
'''
Authr: João Juíz
'''

import sys,sqlalchemy
import pandas as pd
import numpy as np

from sklearn import preprocessing, feature_selection
from myDb import ExtendedDB
from multicolumnlabelencoder import MultiColumnLabelEncoder

DTYPEINT = np.uint16
DTYPEFLOAT = np.float16


def mySafe_sparse_dot(a,b,*args,**kwargs):
    """ workaround for np.dot and sklearn.feature_selection.SelectKBest.fit() """
    print("safe_sparse_dot()")
    return np.dot(a.astype(DTYPEINT),b.astype(DTYPEINT),*args,**kwargs)
feature_selection.univariate_selection.safe_sparse_dot = mySafe_sparse_dot


class Main(object):
    nominalFeatures=["uploaderlink"]
    stringFeatures=["uploaderlink"]
    normalise=True
    encodeNominalFeatures=True
    KBEST = 1500
    max_features_also_favourited = 10e3

    def __init__(self):
        self.db = ExtendedDB(commitOnClose=False)
        
    def __call__(self, normalise="auto"):
        """
        Create normalised feature matrix out of db.
        Handles nominal and string features.
        """
        print("creating matrix")
        if normalise=="auto": normalise=self.normalise
        
        self.db.query("""
            DROP TABLE IF EXISTS temp_features
        """)
        self.db.query("""
            CREATE TEMP TABLE temp_also_favourited AS (
                SELECT a.id, a.id_also
                FROM also_favourited AS a
                INNER JOIN
                (
                    SELECT id_also, count(id_also)
                    FROM also_favourited
                    GROUP BY id_also 
                    --HAVING count(id_also) > 2
                    ORDER BY count(id_also) DESC
                    LIMIT %s
                ) AS b
                ON a.id_also = b.id_also
            )
        """,(self.max_features_also_favourited,))
        self.db.query("""
            CREATE TABLE temp_features AS(
                SELECT 
                    m.id, 
                    m.uploaderlink,
                    m.views,
                    m.favourited,
                    m.time,
                    COALESCE(y.count,0) AS comments,
                    (
                        views
                        *(  1-
                            EXTRACT(epoch FROM AGE(m.time))
                            /(SELECT max(EXTRACT(epoch FROM AGE(medium.time)))+1 FROM medium)
                        )
                        --/(SELECT MAX(views) FROM medium)
                    ) AS views_per_time,
                    (
                        favourited
                        *(  1-
                            EXTRACT(epoch FROM AGE(m.time))
                            /(SELECT max(EXTRACT(epoch FROM AGE(medium.time)))+1 FROM medium)
                        )
                        --/(SELECT MAX(favourited) FROM medium)
                    ) AS favourited_per_time,
                    (
                        COALESCE(y.count,0)
                        *(  1-
                            EXTRACT(epoch FROM AGE(m.time))
                            /(SELECT max(EXTRACT(epoch FROM AGE(medium.time)))+1 FROM medium)
                        )
                        --/(SELECT MAX(favourited) FROM medium)
                    ) AS comments_per_time --,
                    --CASE WHEN (m.id in (SELECT id FROM ids_likes)) THEN 'l'
                    --     WHEN (m.id in (SELECT id FROM ids_dislikes)) THEN 'd'
                    --     ELSE '?'
                    --END AS rating
                FROM medium AS m
                LEFT JOIN (
                    SELECT id, count(id)
                    FROM comments
                    GROUP BY id
                ) AS y
                ON m.id = y.id
                --INNER JOIN (
                --    SELECT * FROM ids_likes
                --    UNION ALL
                --    SELECT * FROM ids_dislikes
                --) AS z
                --ON m.id = z.id
            )
        """)
        self.db.commit()
        
        # table to pandas
        alchemy = sqlalchemy.create_engine('postgresql:///motherless')
        data = pd.read_sql_table("temp_features",alchemy,index_col='id',parse_dates=None)
        
        # filter
        #data = data[:10]
        
        ids = data.index.tolist()

        # stringfeatures to int
        mle = MultiColumnLabelEncoder(columns = self.stringFeatures)
        data = mle.fit_transform(data)
        del mle
        
        # datetime to int
        data["time"] = [d.toordinal() for d in data["time"]]
        
        # X = np.array(data)
        columns = data.columns
        X = data.as_matrix().astype(DTYPEINT)
        del data
        print("\t#features = %d"%X.shape[1])
        
        # nominal features to binary
        if self.encodeNominalFeatures:
                sys.stdout.write("\tNominal features to binary...")
                enc = preprocessing.OneHotEncoder(
                    categorical_features=np.in1d(
                        columns,list(self.nominalFeatures)), 
                    sparse=False,
                    dtype=DTYPEINT)
                X = enc.fit_transform(X).astype(DTYPEINT)
                #columns 
                nominalOrdered = [x for x in columns if x in self.nominalFeatures]
                notNominalOrdered = [x for x in columns if x not in self.nominalFeatures]
                encodedColumns = [col for x,col in enumerate(nominalOrdered) for _ in range(enc.n_values_[x]) ]
                columns = np.concatenate((encodedColumns, notNominalOrdered))
                print("\t#features = %d"%X.shape[1])
                del enc

        # list-features to binary
        for table,select in [("tags","link"),("groups","link"),
                ("temp_also_favourited","id_also")
            ]:
            sys.stdout.write("\t%s... "%table)
            sys.stdout.flush()
            X2, columns2 = self.getListFeatures(table,select,ids)
            sys.stdout.write("\t#features: +%d -> %d..."%(X2.shape[1], X.shape[1]+X2.shape[1]))
            sys.stdout.flush()
            # unite(data,X2)
            #data = data.join(X2,rsuffix=table)
            columns = np.concatenate((columns,columns2))
            X = np.column_stack((X,X2))
            sys.stdout.write("done (%s)\n"%X.dtype)
            sys.stdout.flush()
                
        # set vars
        sys.stdout.write("\tsetting vars\n")
        likes = self.getRatedIds("likes")
        dislikes = self.getRatedIds("dislikes")
        ids_condition = [(i, (i in likes or i in dislikes)) for i in ids]
        ids_train = [i for i,condition in ids_condition if condition == True]
        ids_eval = [i for i,condition in ids_condition if condition == False]
        mask_rated = np.array([condition for _, condition in ids_condition],dtype=np.bool)
        y_train = np.array([int(i in likes) for i in ids_train],dtype=np.uint8)

        # feature selection
        chosen_cols, skb = self.fvTrimmed(X[mask_rated,:], y_train)
        #columns = [columns[x] for x in chosen_cols]
        columns = columns[skb.get_support()]
        X = skb.transform(X)
        del skb

        if normalise:
                X = preprocessing.normalize(X, norm='l2', axis=0).astype(DTYPEFLOAT)
        else:
            X = X.astype(DTYPEFLOAT)
        
        # split labelled and unlabelled samples
        X_train = X[mask_rated,:]
        X_eval = X[np.logical_not(mask_rated),:]
        
        return (X_train, y_train, X_eval, ids_eval, columns)

    def fvTrimmed(self, X, y):
        """ select k best features """
        sys.stdout.write("Feature selection... ")
        sys.stdout.flush()
        skb = feature_selection.SelectKBest(feature_selection.chi2, k=self.KBEST)
        skb.fit(X, y)
        #X = skb.transform(X)
        #columns:
        a=[(idx_,score) for idx_,score in enumerate(skb.scores_) if not np.isnan(score)]
        a=sorted(a,key=lambda x:x[1], reverse=True)
        cols = [idx_ for idx_,score in a[:self.KBEST]]
        print("%d Features"%len(cols))
        #most=[(self.columns[idx_],score) for idx_,score in a[:self.KBEST]]
        return cols, skb
        #args2 = (cols, X, y)+tuple([skb.transform(m) for m in args])
        #return args2
                
    def writeToFile(self, *args, **kwargs):
        """ write all info from __call__ to ./matrix.npz """
        X,y,X_eval,ids,cols = self(*args, **kwargs)
        print("writing file")
        np.savez("matrix.npz",X=X,y=y,X_eval=X_eval,ids=ids,cols=cols)

    def loadFromFile(self):
        """ load matrix from file """
        sys.stdout.write("loading file ")
        npz = np.load("matrix.npz")
        sys.stdout.write("(%s)\n"%npz["X"].dtype)
        return npz["X"], npz["y"], npz["X_eval"], npz["ids"], npz["cols"]
    
    def getRatedIds(self, category="likes"):
        """ return id list of all @category media """
        self.db.query("SELECT id FROM ids_%s"%category)
        return [r["id"] for r in self.db.cursor.fetchall()]
            
    def getListFeatures(self, table, select, ids):
        """
        Create dict with tags and groups for each medium. Transform to binary matrix and return.
        """
        mlb = preprocessing.MultiLabelBinarizer(sparse_output=False)
        multiLabels = []
        for i in ids:
            self.db.query("SELECT "+select+" FROM "+table+" WHERE id=%s",(i,))
            multiLabels.append(set([r[0] for r in self.db.cursor.fetchall()]))
        X2 = mlb.fit_transform(multiLabels).astype(np.uint8)
        return X2, ["%s_%s"%(table,x) for x in mlb.classes_]
        
MatrixFactory = Main
        
if __name__ == "__main__":
    Main()()

