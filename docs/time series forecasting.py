
# I have taken the following dataset from "https://data.open-power-system-data.org/time_series/2020-10-06" with applying date filter
# and specifying the date from 2018-12-25 to 2020-01-01 to make the larger dataset comparatively compact for easier and faster analysis

import pandas as pd
df = pd.read_csv('time_series_15min_singleindex_filtered.csv')
df

# The problem that I have tried to formulate here is trying to predict the missing values for DE_solar_capacity from the other metrices provided such as
# DE_solar_generation_actual,DE_solar_profile for different places(AT, BE, DE) one by one by training a time-series forecasting model using Simple Exponential 
# Smoothing (SES). The trained model would be expected to fill the gaps in the data as the final goal

# visualizing the data
from matplotlib import pyplot
df.plot(figsize=(30, 10))
pyplot.show()

# finding the NaN values in the data for proper understanding and selectively picking up columns for training the model
df.isna().sum()

# let's take a subset of the original dataframe to predict the solar capacity missing values for DE location and later replicating the same for others
# in terms of other metrices such as wind; etc and for different locations
dfNew = df[['utc_timestamp','DE_solar_generation_actual','DE_solar_profile','DE_solar_capacity']]
dfNew

# visualizing this subset dataset
dfNew.plot(figsize=(12, 6))
pyplot.show()

# Oberving the relation between one the feature columns-DE_solar_generation_actual & target DE_solar_capacity
dfy = dfNew.DE_solar_generation_actual
dfx = dfNew.DE_solar_capacity
pyplot.plot(dfx, dfy)
pyplot.ylabel('DE_solar_generation_actual')
pyplot.xlabel('DE_solar_capacity')
pyplot.title('relation between target and feature columns for DE solar')
pyplot.show()

dfNew_final = dfNew
# dfNew_final.dropna()
dfNew_final=dfNew_final[['DE_solar_generation_actual','DE_solar_profile','DE_solar_capacity']]
dfNew_final

dfNew_final.loc[[35615]]
# after this index 'DE_solar_capacity' column has NaN values, so we consider for our test, train data values upto this index

# We now divide the data into test and train, keeping the target column as DE_solar_capacity and the rest as feature columns
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

modelData = dfNew_final.iloc[:35616, :] 
X = modelData.iloc[:, :2]
Y = modelData.iloc[:, 2]
x_train, x_test, y_train, y_test = train_test_split(X,Y, test_size=0.2)

y_test

from sklearn.linear_model import LinearRegression
import numpy as np

model1 = LinearRegression().fit(x_train, y_train)
r_squared = model1.score(x_train, y_train)
r_squared

# from statsmodels.tsa.ar_model import AutoReg
# model2 = AutoReg(np.asarray(y_train), lags=1)
# model2.fit() 
# predicted2 = model2.predict(x_test)
# print("Accuracy Score:")
# print(accuracy_score(y_test, predicted2))

y_pred = model1.predict(x_test)
y_pred
# we can see here that the predicted values differ significantly from the actual values, motivating us to adopt a better prediction method

# Now I have tried to repeat the training model steps with new method-SimpleExpSmoothing which is supposed to give better results than earlier method
# Once the model is fitted, we can further use it to find the prediction/target values as well visualize the predictions for different levels of 
# smoothing as can be seen in the next block of code

from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt 
train = modelData.iloc[100:-10, :]
test = modelData.iloc[-10:, :]
# train.index = pd.to_datetime(train['utc_timestamp'])
# test.index = pd.to_datetime(test['utc_timestamp'])
pred = test.copy()

model = SimpleExpSmoothing(np.asarray(train['DE_solar_capacity']))
# model._index = pd.to_datetime(train.index)

# Now, we use Simple Exponential Smoothing when there are: Few data points, Irregular data, No seasonality or trend. The reason behind this SES only has one
# component called level (with a smoothing parameter denoted as “alpha”). It is a weighted average of the previous level and the current observation
# On the other hand, Holt’s Linear Smoothing is used when there is: Trend in data, No seasonality. 

fig, axes = pyplot.subplots(figsize=(10, 5))
axes.plot(train.DE_solar_capacity[200:], train.values[200:])
axes.plot(test.DE_solar_capacity, test.values, color="blue")
modelfit1 = model.fit()
prediced1 = modelfit1.forecast(10)
modelfit2 = model.fit(smoothing_level=.2)
prediced2 = modelfit2.forecast(10)
modelfit3 = model.fit(smoothing_level=.5)
prediced3 = modelfit3.forecast(10)
for p, f, c in zip((prediced1, prediced2, prediced3),(modelfit1, modelfit2, modelfit3),('#ff8a23','#43763c','c')):
    axes.plot(train.DE_solar_capacity[200:], f.fittedvalues[200:], color=c)
    axes.plot(test.DE_solar_capacity, p, label="alpha="+str(f.params['smoothing_level'])[:3], color=c)
pyplot.title("Simple Exponential Smoothing")    
pyplot.legend();

# Although both the Smoothing algorithms appear similar, they have a slight difference, which. cannot be determined at this point in the dataset chosen.
# There's a posibility of seasonality being present in this data since solar/wind data can vary during different period of the year
# So, for comparison, I have also fitted the model using Holt’s Linear Smoothing after SES and tried to visualize the predictions for better understanding

modelH = Holt(np.asarray(train['DE_solar_capacity']))
# model._index = pd.to_datetime(train.index)

modelfit1H = model.fit(smoothing_level=.3)
pred1H = modelfit1H.forecast(10)
modelfit2H = model.fit(optimized=True)
pred2H = modelfit2H.forecast(10)
modelfit3H = model.fit(smoothing_level=.3)
pred3H = modelfit3H.forecast(10)

fig, axesH = pyplot.subplots(figsize=(10, 5))
axesH.plot(train.DE_solar_capacity[150:], train.values[150:])
axesH.plot(test.DE_solar_capacity, test.values, color="blue")
for p, f, c in zip((pred1H, pred2H, pred3H),(modelfit1H, modelfit2H, modelfit3H),('#ff8a23','#43763c','c')):
    axesH.plot(train.DE_solar_capacity[150:], f.fittedvalues[150:], color=c)
    axesH.plot(test.DE_solar_capacity, p, label="alpha="+str(f.params['smoothing_level'])[:4], color=c)
pyplot.title("Holt's Exponential Smoothing")
pyplot.legend();

# Let's now try to use the above for a new subset of our dataframe- DE wind  
dfDeWind = df[['DE_wind_generation_actual','DE_wind_profile','DE_wind_capacity']]
dfDeWind.isna().sum()

dfDeWind.loc[[35615]]

# visualizing this subset dataset
dfDeWind.plot(figsize=(10, 5))
pyplot.show()

deWindModelData = dfDeWind.iloc[:35616, :] 
trainDeWind = deWindModelData.iloc[100:-10, :]
testDeWind = deWindModelData.iloc[-10:, :]
predDeWind = testDeWind.copy()
modelDeWind = SimpleExpSmoothing(np.asarray(trainDeWind['DE_wind_capacity']))

fig, axes = pyplot.subplots(figsize=(10, 5))
axes.plot(trainDeWind.DE_wind_capacity[200:], trainDeWind.values[200:])
axes.plot(testDeWind.DE_wind_capacity, testDeWind.values, color="pink")
modelDeWindfit1 = modelDeWind.fit()
prediced1 = modelfit1.forecast(10)
modelDeWindfit2 = modelDeWind.fit(smoothing_level=.2)
prediced2 = modelfit2.forecast(10)
modelDeWindfit3 = modelDeWind.fit(smoothing_level=.5)
prediced3 = modelfit3.forecast(10)
for p, f, c in zip((prediced1, prediced2, prediced3),(modelDeWindfit1, modelDeWindfit2, modelDeWindfit3),('#ff8a23','#43763c','c')):
    axes.plot(trainDeWind.DE_wind_capacity[200:], f.fittedvalues[200:], color=c)
    axes.plot(testDeWind.DE_wind_capacity, p, label="alpha="+str(f.params['smoothing_level'])[:3], color=c)
pyplot.title("Simple Exponential Smoothing")    
pyplot.legend();

modelDeWindH = Holt(np.asarray(trainDeWind['DE_wind_capacity']))

modelDeWindfit1H = modelDeWindH.fit(smoothing_level=.3)
predDEW1H = modelDeWindfit1H.forecast(10)
modelDeWindfit2H = modelDeWindH.fit(optimized=True)
predDEW2H = modelDeWindfit2H.forecast(10)
modelDeWindfit3H = modelDeWindH.fit(smoothing_level=.3)
predDEW3H = modelDeWindfit3H.forecast(10)

fig, axesH = pyplot.subplots(figsize=(10, 5))
axesH.plot(trainDeWind.DE_wind_capacity[150:], trainDeWind.values[150:])
axesH.plot(testDeWind.DE_wind_capacity, testDeWind.values, color="pink")
for p, f, c in zip((predDEW1H, predDEW2H, predDEW3H),(modelDeWindfit1H, modelDeWindfit2H, modelDeWindfit3H),('#ff8a23','#43763c','c')):
    axesH.plot(trainDeWind.DE_wind_capacity[150:], f.fittedvalues[150:], color=c)
    axesH.plot(testDeWind.DE_wind_capacity, p, label="alpha="+str(f.params['smoothing_level'])[:4], color=c)
pyplot.title("Holt's Exponential Smoothing")
pyplot.legend();

# The equations below mathematically show the difference between SES and Holt's linear smoothing
# For images please refer img folder in the repository

# This reference image shows how the two smoothing algorithms would be performing in comparison with each other
# (source: https://towardsdatascience.com/time-series-in-python-exponential-smoothing-and-arima-processes-2c67f2a52788)
# For images please refer img folder in the repository

# Comparing the proposed methods here with other time series classical forecasting methods, Exponential smoothings methods are appropriate for 
# non-stationary data (ie data with a trend and seasonal data) which might to be more apt in this scenerio. On the contrary, some commonly used 
# other methods like ARIMA models should be used on stationary data only. One has to then remove the trend of the data (via deflating 
# or logging), and then look at the differenced series.
# Exponential would be considered better that ARIMA due to its weight assigning method.
