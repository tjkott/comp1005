import matplotlib.pyplot as plt
#import module from matplot library
import pandas as pd
#import pandas library and alias pd
df = pd.read_csv('march4.csv')
print(df.head())
#Head() method displays first 5 rows of the dataframe. 
Print(df("9am").describe())
#selects the column named "9am" from the dataframe. 
plt.figure(figsize=(10, 5))
# sets the 10 wide and 5 tall. 
ddf["Minimum"].plot()
#plots the "Minimum" column of the dataframe.
plt.show()
#displays the plot