# Importing required libraries
import datetime as dt
import pandas as pd

# Setting row and column views
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 150)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# 2010-2011 Data
df_ = pd.read_excel(r'C:\Users\Lenovo\Desktop\DSMLBC5\datasets\online_retail_II.xlsx', sheet_name='Year 2010-2011')
df = df_.copy()
df.head()

### DATA EXAMINATION & PREPARATION

df.info()
df.shape
df.describe().T
df.isnull().sum()

# Discarding missing values
df.dropna(inplace=True)
df.isnull().sum()

# Unique number of products
df["StockCode"].nunique()

# How many of each product are there?
df['StockCode'].value_counts().head()

# Sorting the 5 most ordered products from most to least
# It makes more sense to use stock code here, there may be typos in the description.
df_most = df.groupby('StockCode').agg({'Quantity': 'count'}).sort_values('Quantity', ascending=False)
df_most.head(5)

# The 'C' in invoices shows canceled transactions. Removal of canceled transactions from the dataset
# Canceled transactions
df[df['Invoice'].str.contains("C", na = False)]
# Removal of canceled transactions
df[~df['Invoice'].str.contains("C", na = False)]

# 'TotalPrice' represents the total earnings per invoice
df = df[df["Quantity"] > 0]
df = df[df["Price"] > 0]
df["TotalPrice"] = df["Quantity"] * df["Price"]
df.tail()


### CALCULATING RFM METRICS

# recency : Time since last purchase (in days)
# frequency : Frequency of purchase
# monetary : Total money earned by the customer

# InvoiceDate
df["InvoiceDate"].max()

today_date = dt.datetime(2011, 12, 11)
# Invoice
# Total Price : Total earnings by invoices
rfm = df.groupby('Customer ID').agg({'InvoiceDate' : lambda InvoiceDate : (today_date - InvoiceDate.max()).days,
                                     'Invoice' : lambda Invoice : Invoice.nunique(),
                                     'TotalPrice' : lambda TotalPrice : TotalPrice.sum()})

# Changing the created metric names
rfm.columns  = ['recency', 'frequency', 'monetary']
# Subtracting negative values because the Monetary value cannot be negative
rfm = rfm[rfm["monetary"] > 0]
rfm.head()


### CALCULATING RFM SCORES

# Recency
rfm['recency_score'] = pd.qcut(rfm['recency'], 5, labels = [5,4,3,2,1])
# Frequency
rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method = 'first'), 5, labels = [1,2,3,4,5])
# Monetary
rfm['monetary_score'] = pd.qcut(rfm['monetary'], 5, labels = [1,2,3,4,5])

# It is more important to know the customer's purchase frequency and how long they have not shopped
rfm["RFM_SCORE"]  = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))
rfm.head()


#### CREATING & ANALYSING RFM SEGMENTS

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}
rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm.head()

# Analysis of RFM segments on the basis of mean and number
rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

# Examining Loyal Customers Segment
rfm[rfm["segment"] == "loyal_customers"].head()

# Indexes of loyal customers
new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"]== "loyal_customers"].index
new_df

# Save as a csv
new_df.to_csv("loyal_customers.csv")