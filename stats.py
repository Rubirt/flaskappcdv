import pandas as pd
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import matplotlib
import matplotlib.pyplot as plt
import os

matplotlib.use('Agg')

def analyse(df,path):
    dfr = pd.DataFrame(columns=['Column','Type', 'Unique','IsNul', 'NaNs','Min','Average','Max','Median','Standard Deviation', "First Date", "Last Date","Histogram"])
    for col in df.columns:    
        if is_numeric_dtype(df[col]):
            fig, ax = plt.subplots()
            df.hist(col, ax=ax)
            re = path.replace(".","")
            file = os.path.join(path,col.replace(" ","").replace(":","")+'.png')
            filepath = os.path.join(re,col.replace(" ","").replace(":","")+'.png')
            fig.savefig(file)
            plt.close(fig)
            data = {"Column":col, "Type":df.dtypes[col], "Min":df[col].min(),"Average":df[col].mean(), "Max":df[col].max(), "Median":df[col].median(), "Standard Deviation":df[col].std(), "Histogram":filepath}
            dfr = dfr.append(data, ignore_index=True)
        elif is_string_dtype(df[col]):
            data = {"Column":col, "Type":df.dtypes[col], "IsNul":df[col].isnull().sum(),"NaNs":df[col].isna().sum(),"Unique":len(df[col].unique())}
            dfr = dfr.append(data, ignore_index=True)
            
        elif is_datetime(df[col]):
            data = {"Column":col, "Type":df.dtypes[col], "First Date":df[col].min().date().strftime("%d %b %Y"), "Last Date":df[col].max().date().strftime("%d %b %Y")}
            dfr = dfr.append(data, ignore_index=True)

            
    dfr.to_csv(os.path.join(path,"result.csv"),sep=';', index=False)


