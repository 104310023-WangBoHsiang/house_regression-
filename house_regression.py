# -*- coding: utf-8 -*-
"""House_Regression.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tAZKEFFAVFiiprDe8MkJAZpI-KLzGJs3
"""
'''
from google.colab import drive
drive.mount('/content/drive')
# login and enter the Authorization code
# 登入並且輸入授權碼
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler # Used for scaling of data
from sklearn.model_selection import train_test_split

# Read dataset into X and Y
df_train = pd.read_csv("D:/download/database/train-v3.csv")
df_valid = pd.read_csv('D:/download/database/valid-v3.csv')
df_test = pd.read_csv('D:/download/database/test-v3.csv')

df_train.head()

df_valid.head()

sns.distplot(df_train['price']);

#correlation matrix
corrmat = df_train.corr()
f, ax = plt.subplots(figsize=(12, 9))
sns.heatmap(corrmat, vmax=.8, square=True);

#saleprice correlation matrix
k = 20 #number of variables for heatmap
cols = corrmat.nlargest(k, 'price')['price'].index
cm = np.corrcoef(df_train[cols].values.T)
plt.figure(figsize = (16,10))
sns.set(font_scale=1.25)
hm = sns.heatmap(cm, cbar=True, annot=True, square=True, fmt='.2f', annot_kws={'size': 10}, yticklabels=cols.values, xticklabels=cols.values)
plt.show()


cols = ['price','bedrooms',
       'bathrooms', 'sqft_living', 'sqft_lot', 'floors', 'waterfront', 'view',
       'condition', 'grade', 'sqft_above', 'sqft_basement', 'yr_built',
       'yr_renovated', 'lat', 'long', 'sqft_living15',
       'sqft_lot15']
select_col = ['bedrooms',
       'bathrooms', 'sqft_living', 'sqft_lot', 'floors', 'waterfront', 'view',
       'condition', 'grade', 'sqft_above', 'sqft_basement', 'yr_built',
       'yr_renovated', 'lat', 'long', 'sqft_living15',
       'sqft_lot15']

df_train = df_train[cols]
df_train = pd.get_dummies(df_train)
df_train = df_train.fillna(df_train.mean())
df_valid = df_valid[cols]
df_valid = pd.get_dummies(df_valid)
df_valid = df_valid.fillna(df_valid.mean())

df_test = pd.get_dummies(df_test)
df_test = df_test.fillna(df_test.mean())

scale = StandardScaler()
X_train = df_train[select_col]
X_train = scale.fit_transform(X_train)
X_valid = df_valid[select_col]
X_valid = scale.fit_transform(X_valid)
X_test = df_test[select_col]
X_test = scale.fit_transform(X_test)

# Y is just the 'price' column
Y_train = df_train['price'].values

Y_valid = df_valid['price'].values


# Define the neural network
from keras.models import Sequential
from keras.layers import Dense,Dropout,BatchNormalization
from keras import metrics
from keras import optimizers



def create_model():
    # create model
    model = Sequential()

    model.add(Dense(17, input_dim=X_train.shape[1], activation='relu'))
    model.add(BatchNormalization())
    #model.add(Dropout(0.1))
    model.add(Dense(64, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(0.1))
    model.add(Dense(128, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(0.1))    
    model.add(Dense(256, activation='relu'))
    model.add(BatchNormalization())      
    
    model.add(Dense(1))
    
    # Compile model
    Adadelta = optimizers.Adadelta(lr=5)
    
    model.compile(optimizer = Adadelta , loss = 'mean_absolute_error', metrics =[metrics.mae])
    return model

model = create_model()
model.summary()

from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint,ReduceLROnPlateau

checkpointer = ModelCheckpoint(filepath='D:/download/database/model_Adadelta_test.h5', verbose=1, save_best_only=True)
early_stopping = EarlyStopping(monitor='val_loss', patience=500)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5,patience=100, min_lr=0.0001,verbose=1,cooldown = 1)

history = model.fit(X_train, Y_train, validation_data=(X_valid,Y_valid), epochs=300000, batch_size=2048,callbacks=[checkpointer,early_stopping,reduce_lr])


from keras.models import load_model
#del model  # 删除现有模型
'''
try:
    model = load_model('D:/download/database/model_Adadelta_63814.65450_256.h5')
    print("載入模型成功!繼續訓練模型")
except :    
    print("載入模型失敗!開始訓練一個新模型")


loss, accuracy = model.evaluate(X_valid,Y_valid)

print(loss)

print(accuracy)

'''
ynew = model.predict(X_test, batch_size=None, verbose=1, steps=None)

# show the inputs and predicted outputs
for i in range(len(X_test)):
	print("X=%s, Predicted=%s" % (X_test[i], ynew[i]))

# summarize history for accuracy
plt.plot(history.history['mean_absolute_error'])
plt.plot(history.history['val_mean_absolute_error'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

##############################################################################
import xgboost as xgb
from sklearn.metrics import mean_squared_error,median_absolute_error

regr = xgb.XGBRegressor(
                 colsample_bytree=0.5,
                 gamma=0.5,
                 learning_rate=0.001,
                 max_depth=9,
                 min_child_weight=10,
                 n_estimators=300000,                                                                  
                 reg_alpha=0.9,
                 reg_lambda=0.9,
                 subsample=0.5,
                 seed=42,
                 silent=0)
params={
        'objective':'reg:linear',
        'colsample_bytree': 0.7,
        'min_child_weight':2,
        'gamma':0,
        'subsample':0.9,
        'scale_pos_weight':1,
        'learning_rate': 0.0001, 
        'max_depth': 9,
        'alpha': 1,
        'eval_metric':'mae'
        }

dtrain=xgb.DMatrix(X_train,label=Y_train)
dvalid=xgb.DMatrix(X_valid, Y_valid)
dtest=xgb.DMatrix(X_test)
regr.fit(X_train, Y_train, early_stopping_rounds=1000, eval_metric="mae", eval_set=[(X_valid, Y_valid)], verbose=True,)


y_pred_62334 = regr.predict(X_test, ntree_limit=regr.best_ntree_limit)
y_pred_ = regr.predict(X_test)

submit = pd.DataFrame()
submit['ID'] = df_test['id'].values
submit['price'] = y_pred_62334
submit.head()
submit.to_csv('D:/download/database/pred_results62334.csv', index = False)


#print('均方根误差:',median_absolute_error(Y_valid,y_pred))

######################################################
pred_Y_train = regr.predict(X_train, ntree_limit=regr.best_ntree_limit)
plt.scatter(Y_train,pred_Y_train)
print('MAE:',median_absolute_error(Y_train,pred_Y_train))

pred_Y_valid = regr.predict(X_valid, ntree_limit=regr.best_ntree_limit)
plt.scatter(Y_valid,pred_Y_valid)
print('MAE:',median_absolute_error(Y_valid,pred_Y_valid))



plt.figure(figsize=(20,8))
for i in range(6):
    ii = '23'+str(i+1)
    plt.subplot(ii)
    feature = select_col[i+12]
    plt.scatter(df_test[feature], ynew, facecolors='none',edgecolors='k',s = 75)
    sns.regplot(x = feature, y = ynew, data = df_test,scatter=False, color = 'Blue')
    plt.ylabel('price')
    ax=plt.gca() 
    #ax.set_ylim([0,800000])

plt.scatter(df_valid,pred_Y_valid, label='prediction')
plt.scatter(X_test,ynew, facecolors='none',edgecolors='k',s = 75)
sns.regplot(x = X_test, y = ynew, data = df_test,scatter=False, color = 'Blue')
plt.legend()
plt.show()


########################################################
xgb.plot_importance(regr) 
plt.rcParams['figure.figsize'] = [15, 15] 
plt.show()



