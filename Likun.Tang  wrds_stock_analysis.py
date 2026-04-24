import wrds
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# connect WRDS
db = wrds.Connection()

# query data
query = """
SELECT date, permno, ret, prc, vol
FROM crsp.msf
WHERE date BETWEEN '2020-01-01' AND '2022-12-31'
LIMIT 30000
"""

df = db.raw_sql(query)

# clean data
df = df.dropna()

# calculate risk (std) and return (mean)
summary = df.groupby('permno').agg({
    'ret': 'mean'
}).rename(columns={'ret': 'mean_return'})

summary['risk'] = df.groupby('permno')['ret'].std()

summary = summary.dropna().reset_index()

# classify risk
def classify_risk(risk):
    if risk < summary['risk'].quantile(0.33):
        return "Low"
    elif risk < summary['risk'].quantile(0.66):
        return "Medium"
    else:
        return "High"

summary['risk_level'] = summary['risk'].apply(classify_risk)

# basic python structures
returns_list = summary['mean_return'].tolist()
risk_dict = dict(zip(summary['permno'], summary['risk']))
sample_tuple = (returns_list[0], returns_list[1])

count = 0
for r in returns_list:
    if r > 0:
        count += 1

print("Positive-return stocks:", count)

# plot
plt.scatter(summary['risk'], summary['mean_return'])
plt.xlabel('Risk')
plt.ylabel('Return')
plt.title('Risk vs Return')
plt.show()

# save
summary.to_excel("result.xlsx", index=False)
