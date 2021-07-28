from category_encoders import CountEncoder
import dill
from sklearn import preprocessing
import pandas as pd
from sklearn.model_selection import KFold, GridSearchCV, cross_validate,train_test_split
from sklearn.pipeline import Pipeline
from xgboost.sklearn import XGBRegressor
from matplotlib import  pyplot
import os
import matplotlib.pyplot as plt
import numpy as np
full_data=pd.read_csv("../data/data_cars.csv")
features, target = full_data.drop(columns=['price']), full_data['price']
X_train,X_test,y_train,y_test=train_test_split(features,target,shuffle=True,test_size=0.02)
pd.DataFrame(X_train).to_csv('./X_train.csv',index=False)
pd.DataFrame(X_test).to_csv('./X_test.csv',index=False)
pd.DataFrame(y_train).to_csv('./y_train.csv',index=False)
pd.DataFrame(y_test).to_csv('./y_test.csv',index=False)
categorical_columns = X_train.select_dtypes(object).columns
scoring=['r2', 'neg_root_mean_squared_error']

pipeline = Pipeline(steps=[('encoder', CountEncoder(cols=categorical_columns,
                                                        min_group_size=1,
                                                        handle_unknown=0)),
                               ('regressor', XGBRegressor(n_estimators=1000,
                                                          verbosity=0,
                                                          reg_lambda=0.4,
                                                          reg_alpha=0.4,
                                                          sample_type='uniform',
                                                          rate_drop=0.1,
                                                          base_score=0.5,
                                                          booster='gbtree',
                                                          subsample=1,
                                                          colsample_bylevel=1,
                                                          colsample_bynode=1,
                                                          colsample_bytree=1,
                                                          gamma=0.1,
                                                          importance_type='gain',
                                                          max_delta_step=0,
                                                          min_child_weight=1,
                                                          n_jobs=4,
                                                          objective='reg:squarederror',
                                                          max_depth=4,
                                                          learning_rate=0.07,
                                                          random_state=5))])
params = {
    'regressor__n_estimators' : [700,1000,1500,2000],
    'regressor__max_depth' : [4,5,6],
    'regressor__learning_rate' : [0.03,0.07,0.11],
    'regressor__reg_lambda':[0.4],
    'regressor__reg_alpha':[0.4],
    'regressor__gamma':[0.1],
    'regressor__rate_drop':[0,0.3],
    'regressor__subsample':[1]
}
kfold_generator = KFold(n_splits=10, shuffle=True, random_state=5)
search = GridSearchCV(pipeline, params, cv=kfold_generator, scoring=scoring, n_jobs=4, verbose=0, refit='neg_root_mean_squared_error')
search.fit(X_train,y_train)
search_res=pd.DataFrame(search.cv_results_)
search_res.to_excel('./optimization.xlsx')
print(search_res[['mean_test_neg_root_mean_squared_error']])
best_model = search.best_estimator_
X_test['prediction']=best_model.predict(X_test)
X_test['true_value']=y_test
X_test.to_csv('./comparison_results.csv',index=False)
dill.dump(best_model, open('./Xgboost_model.pkl', 'wb'))