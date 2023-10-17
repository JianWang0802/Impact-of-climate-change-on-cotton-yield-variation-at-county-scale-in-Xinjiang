import pandas as pd
import numpy as np
from scipy.stats import norm
from sklearn.linear_model import LinearRegression
import os
os.chdir(r'E:\Data')


# Define a function to perform the Mann-Kendall test. This function will take an array of time series data as input and
# return the statistics and p-values of the Mann-Kendall test.
def trend_analysis(data):
    regions = data['Region']
    # lats = data['lat']
    # lngs = data['lng']
    mk_z = []
    mk_p = []
    sen_slope_val = []
    for i in range(len(data)):
        x = data.iloc[i, 0:].values
        # Mann-Kendall test
        s = 0
        for j in range(len(x) - 1):
            for k in range(j + 1, len(x)):
                s += np.sign(x[k] - x[j])
        var_s = len(x) * (len(x) - 1) * (2 * len(x) + 5) / 18
        if s > 0:
            z = (s - 1) / np.sqrt(var_s)
        elif s < 0:
            z = (s + 1) / np.sqrt(var_s)
        else:
            z = 0
        p = 2 * (1 - norm.cdf(abs(z)))
        mk_z.append(z)
        mk_p.append(p)
        # Sen's slope method
        slopes = []
        for j in range(len(x) - 1):
            for k in range(j + 1, len(x)):
                slope = (x[k] - x[j]) / (k - j)
                slopes.append(slope)
        sen_slope_val.append(np.median(slopes))

# result = pd.DataFrame({'Region': regions, 'lat': lats, 'lng': lngs, 'Mann-Kendall Z': mk_z, 'Mann-Kendall p': mk_p,
    #                        'Sen\'s Slope': sen_slope_val})
    result = pd.DataFrame({'Mann-Kendall Z': mk_z, 'Mann-Kendall p': mk_p,
                           'Sen\'s Slope': sen_slope_val})
    return result


data = pd.read_csv('output.csv', encoding='gbk')
# Call the trend_analysis function and calculate the trend value
result = trend_analysis(data)
# print(result)
# x = np.array(data.columns[0:].values, dtype=np.float64)
# print(x)

for i in range(len(result)):
    y = np.array(data.iloc[i, 0:].values, dtype=np.float64)
    # print(y)
    x = x.reshape(-1, 1)
    model = LinearRegression().fit(x, y)
    slope = model.coef_[0]
    intercept = model.intercept_
    for j in range(31):
        print(data.iloc[i, 0])
        trend_val = data.iloc[i, 0] + data.iloc[i, j] - slope * x[j] - intercept
        # print(trend_val)
        result.loc[i, str(x[j])] = trend_val
#
#
# # print(result)
# # save result
result.to_csv('result.csv', index=False, encoding='gbk')