#!/usr/bin/env python
# coding: utf-8

# # Installing Libraries

# In[1]:


import pandas as pd
import pymongo
import plotly.express as px
from io import BytesIO


# # Connection to Mongodb Atlas

# In[2]:


mongodb_url = "mongodb+srv://root:root1234@cluster1.yaagwlq.mongodb.net/"
client = pymongo.MongoClient(mongodb_url)
db = client.get_database("sample_airbnb")
collection = db.get_collection("listingsAndReviews")


# In[3]:


document = collection.find_one()
print(document)


# # Retrieving data collection from MongoDB Atlas

# In[4]:


documents = collection.find({})
for document in documents:
    print(document)


# # Fetching important columns for the Initial Table

# In[5]:


data = []
for i in collection.find( {}, {'_id':1, 'name':1,'property_type':1,'room_type':1,'bed_type':1,
                        'minimum_nights':1,'maximum_nights':1,'cancellation_policy':1,'accommodates':1,
                        'bedrooms':1,'beds':1,'number_of_reviews':1,'bathrooms':1,'price':1,
                        'cleaning_fee':1,'extra_people':1,'guests_included':1,'images.picture_url':1, 
                        'review_scores.review_scores_rating':1} ):
    data.append(i)


# In[6]:


df = pd.DataFrame(data)
df


# # Basic Stats of the dataframe

# In[7]:


df.shape


# In[8]:


df.describe().T


# In[9]:


df.info()


# # Data Pre-processing

# ### Extract 'images' & 'review_scores'

# In[10]:


df['images'] = [x.get('picture_url', '') if isinstance(x, dict) else x for x in df['images']]
df.head(2)


# In[11]:


df['review_scores'] = [x.get('review_scores_rating', '') if isinstance(x, dict) else x for x in df['review_scores']]
df.head(2)


# ## Checking for null values

# In[12]:


df['bedrooms'].mean()


# In[13]:


df.isnull().sum()


# In[14]:


df['beds'].mean()


# In[15]:


df['cleaning_fee']


# # Handling missing values

# In[16]:


df['bedrooms'].fillna(0, inplace=True)
df['beds'].fillna(0, inplace=True)
df['bathrooms'].fillna(0, inplace=True)
df['cleaning_fee'].fillna('Not Specified', inplace=True)  
df.isnull().sum()


# In[17]:


df.dtypes


# # Converting Datatypes

# In[18]:


df['minimum_nights'] = df['minimum_nights'].astype(int)
df['maximum_nights'] = df['maximum_nights'].astype(int)
df['bedrooms'] = df['bedrooms'].astype(int)
df['beds'] = df['beds'].astype(int)
df['bathrooms'] = df['bathrooms'].astype(str).astype(float)
df['price'] = df['price'].astype(str).astype(float).astype(int)
df['cleaning_fee'] = df['cleaning_fee'].apply(lambda x: int(float(str(x))) if x != 'Not Specified' else 'Not Specified')
df['extra_people'] = df['extra_people'].astype(str).astype(float).astype(int)
df['guests_included'] = df['guests_included'].astype(str).astype(int)


# In[19]:


df.dtypes


# In[20]:


df.describe().T


# ### Check for Duplicates

# In[21]:


# Check for duplicates in the DataFrame
num_duplicates = df.duplicated().sum()
print("Number of Duplicates:", num_duplicates)


# # Address Table

# In[22]:


address = []
for i in collection.find( {}, {'_id':1, 'address':1}):
    address.append(i)

df_address = pd.DataFrame(address)
address_keys = list(df_address.iloc[0,1].keys())

for i in address_keys:
    if i == 'location':
        df_address['location_type'] = df_address['address'].apply(lambda x: x['location']['type'])
        df_address['longitude'] = df_address['address'].apply(lambda x: x['location']['coordinates'][0])
        df_address['latitude'] = df_address['address'].apply(lambda x: x['location']['coordinates'][1])
        df_address['is_location_exact'] = df_address['address'].apply(lambda x: x['location']['is_location_exact'])
    else:
        df_address[i] = df_address['address'].apply(lambda x: x[i] if x[i]!='' else 'Not Specified')

df_address.drop(columns=['address'], inplace=True)
df_address.head(2)


# In[23]:


df_address['is_location_exact'] = df_address['is_location_exact'].map({False:'No',True:'Yes'})
df_address.head()


# In[24]:


df_address.isnull().sum()


# In[25]:


df_address.duplicated().sum()


# In[26]:


df_address.dtypes


# # Host Table

# In[27]:


# Initialize an empty list to store the data
host_data = []

# Fetch data from the MongoDB collection
for record in collection.find({}, {'_id': 1, 'host': 1}):
    host_data.append(record)

# Create a DataFrame from the extracted data
df_host = pd.DataFrame(host_data)

# List of keys to extract from the 'host' column
host_keys = ['host_id', 'host_name', 'host_location', 'host_response_time', 'host_thumbnail_url', 
             'host_picture_url', 'host_neighbourhood', 'host_response_rate', 'host_is_superhost', 
             'host_has_profile_pic', 'host_identity_verified', 'host_listings_count', 
             'host_total_listings_count', 'host_verifications']

# Extract data from the 'host' column and handle missing keys
for key in host_keys:
    if key == 'host_response_time':
        df_host[key] = df_host['host'].apply(lambda x: x.get(key, 'Not Specified') if isinstance(x, dict) and key in x else 'Not Specified')
    else:
        df_host[key] = df_host['host'].apply(lambda x: x.get(key, 'Not Specified') if isinstance(x, dict) and key in x and x[key] != '' else 'Not Specified')

# Drop the original 'host' column
df_host.drop(columns=['host'], inplace=True)

# Display the DataFrame
df_host.head()


# In[28]:


df_host['host_is_superhost'] = df_host['host_is_superhost'].map({False:'No',True:'Yes'})
df_host['host_has_profile_pic'] = df_host['host_has_profile_pic'].map({False:'No',True:'Yes'})
df_host['host_identity_verified'] = df_host['host_identity_verified'].map({False:'No',True:'Yes'})
df_host.head()


# In[29]:


df_host.isnull().sum()


# In[30]:


df_host.dtypes


# # Availability Table

# In[31]:


availability = []
for i in collection.find( {}, {'_id':1, 'availability':1}):
    availability.append(i)

df_availability = pd.DataFrame(availability)
availability_keys = list(df_availability.iloc[0,1].keys())

for i in availability_keys:
    df_availability['availability_30'] = df_availability['availability'].apply(lambda x: x['availability_30'])
    df_availability['availability_60'] = df_availability['availability'].apply(lambda x: x['availability_60'])
    df_availability['availability_90'] = df_availability['availability'].apply(lambda x: x['availability_90'])
    df_availability['availability_365'] = df_availability['availability'].apply(lambda x: x['availability_365'])

df_availability.drop(columns=['availability'], inplace=True)
df_availability.head()


# In[32]:


df_availability.isnull().sum()


# In[33]:


df_availability.dtypes


# In[34]:


df_availability.duplicated().sum()


# # Amenities Table

# In[35]:


amenities = []
for i in collection.find( {}, {'_id':1, 'amenities':1}):
    amenities.append(i)

df_amenities = pd.DataFrame(amenities)
df_amenities.head()


# In[36]:


# Apply sorting to the 'amenities' column
df_amenities['amenities'] = df_amenities['amenities'].apply(lambda x: sorted(x))

# Display the DataFrame
df_amenities.head()


# In[37]:


df_amenities.isnull().sum()


# In[38]:


df_amenities.dtypes


# ### Merging/joining all dataframes to a single dataframe

# In[39]:


df_new = pd.merge(df, df_host, on='_id')
df_new = pd.merge(df_new, df_address, on='_id')
df_new = pd.merge(df_new, df_availability, on='_id')
df_new = pd.merge(df_new, df_amenities, on='_id')
df_new.head()
     


# In[41]:


df_new.columns


# In[42]:


df_new.dtypes


# In[43]:


df_new.describe()


# In[44]:


#Convert datatypes and round-off decimal places
df_new['minimum_nights'] = df_new['minimum_nights'].round()
df_new['maximum_nights'] = df_new['maximum_nights'].round(1).astype(int)
df_new['accommodates'] = df_new['accommodates'].round().astype(int)
df_new['bedrooms'] = df_new['bedrooms'].round().astype(int)
df_new['beds'] = df_new['beds'].round().astype(int)
df_new['number_of_reviews'] = df_new['number_of_reviews'].round().astype(int)
df_new['bathrooms'] = df_new['bathrooms'].round().astype(int)
df_new['price'] = df_new['price'].round(2).astype(float)
df_new['extra_people'] = df_new['extra_people'].round().astype(int)
df_new['guests_included'] = df_new['guests_included'].round().astype(int)
df_new['host_listings_count'] = df_new['host_listings_count'].round().astype(int)
df_new['host_total_listings_count'] = df_new['host_total_listings_count'].round().astype(int)
df_new['longitude'] = df_new['longitude'].round(2).astype(float)
df_new['latitude'] = df_new['latitude'].round(2).astype(float)
df_new['availability_30'] = df_new['availability_30'].round().astype(int)
df_new['availability_60'] = df_new['availability_60'].round().astype(int)
df_new['availability_90'] = df_new['availability_90'].round().astype(int)
df_new['availability_365'] = df_new['availability_365'].round().astype(int)


# # Data Visualization

# In[46]:


get_ipython().run_line_magic('matplotlib', 'inline')
import seaborn as sns
import matplotlib.pyplot as plt


# In[47]:


# Calculate the correlation matrix
correlation_matrix = df_new.corr(numeric_only=True)

# Create a heatmap to visualize the correlation matrix
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=.5)
plt.title('Correlation Matrix')
plt.show()


# In[48]:


df_new['property_type'].unique()


# In[49]:


from wordcloud import WordCloud

# Assuming df_new is your DataFrame
property_types_text = ' '.join(df_new['property_type'].astype(str))

wordcloud = WordCloud(width=600, height=400, background_color='white').generate(property_types_text)

plt.figure(figsize=(10, 4))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Different Property Types')
plt.show()


# In[50]:


# Calculate the frequency of each property type and get the top 10 in descending order
top_property_types_counts = df_new['property_type'].value_counts().head(10)

# Display the top property types and their counts
print(top_property_types_counts)


# In[51]:


total_property_types = df_new['property_type'].nunique()
print("Total number of property types:", total_property_types)


# In[52]:


df_new['property_type'].value_counts()


# In[53]:


# Create a Horizontal Bar Chart for the top 10 Property Types
fig = px.bar(top_property_types_counts, x='count', title="Top 10 Property Types Distribution")

# Customize the bar color
fig.update_traces(marker_color='darkblue')  # Set the bar color to dark blue

# x and y axes
fig.update_layout(xaxis_title="Count", yaxis_title="Property Type")

# Display the chart
fig.show()


# In[56]:


# sort the DataFrame by the 'number_of_reviews' column in descending order.
df_sorted = df_new.sort_values(by='number_of_reviews', ascending=False)

# select the top N properties (e.g., top 10) with the most reviews.
top_N = 10
top_properties = df_sorted.head(top_N)

# Define a list of 10 distinct colors
custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# Create an interactive horizontal bar chart with hover text.
fig = px.bar(top_properties, x='number_of_reviews', y='name', text='number_of_reviews',
             orientation='h', title=f'Top {top_N} Properties with Most Reviews',
             labels={'number_of_reviews': 'Number of Reviews', 'name': 'Property Name'},
             color='name', color_discrete_map={name: color for name, color in zip(top_properties['name'], custom_colors)})

# Customize the appearance of the chart.
fig.update_traces(texttemplate='%{text}', textposition='inside', textfont_size=14)

# Remove the legend from the chart.
fig.update_layout(showlegend=False)

# Show the chart interactively.
fig.show()


# In[57]:


# Count the number of properties with reviews
count_properties_with_reviews = df_new[df_new['number_of_reviews'] > 0].shape[0]

# Count the number of properties without reviews
count_properties_without_reviews = df_new[df_new['number_of_reviews'] == 0].shape[0]

# Create a bar chart
fig, ax = plt.subplots(figsize=(8, 6))

# Plot the bars
bars = ax.bar(['With Reviews', 'Without Reviews'], [count_properties_with_reviews, count_properties_without_reviews], color=['blue', 'gray'])

# Display the count values inside the bars
for bar in bars:
    yval = bar.get_height()
    plt.annotate(str(int(yval)), xy=(bar.get_x() + bar.get_width() / 2, yval), xytext=(0, 3),
                 textcoords='offset points', ha='center', va='bottom', color='black')

ax.set_ylabel('Number of Properties')
ax.set_title('Number of Properties with and without Reviews')

plt.show()


# In[59]:


# Calculate the counts of superhost and non-superhost
superhost_counts = df_new['host_is_superhost'].value_counts()

# Create a Host Superhost Status Pie Chart
fig = px.pie(superhost_counts, names=superhost_counts.index, values=superhost_counts.values, title="Host Superhost Status", color_discrete_sequence=['lightblue', 'red'])

# Display the chart
fig.show()


# In[60]:


# Calculate the counts of host identity verified and not verified
host_verified_counts = df_new['host_identity_verified'].value_counts()

# Create a Host Identity Verified Pie Chart
fig = px.pie(names=host_verified_counts.index, values=host_verified_counts.values,
             title="Host Verified Status", color_discrete_sequence=['lightgreen', 'red'])

# Display the chart
fig.show()


# In[61]:


# Calculate the frequency of each superhost status for each host
superhost_counts = df_new.groupby(['host_name', 'host_is_superhost']).size().unstack(fill_value=0)

# Find the top 10 superhosts
top_10_superhosts = superhost_counts['Yes'].nlargest(10)

# Define a list of 10 distinct colors
custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# Create a Bar Chart for the top 10 Superhosts
fig = px.bar(x=top_10_superhosts.index, y=top_10_superhosts.values, title="Top 10 Superhosts",
             color=top_10_superhosts.index, color_discrete_map={host: color for host, color in zip(top_10_superhosts.index, custom_colors)})

# Display the chart
fig.show()


# In[62]:


# Group by 'host_response_time' and calculate the count
df_counts = df_new.groupby('host_response_time').size().reset_index(name='count')

# Create the pie chart
fig = px.pie(df_counts, names='host_response_time', values='count', hole=0.5, title="Host Response Time",
             color_discrete_sequence=px.colors.qualitative.Set1)

fig.update_traces(text=df_counts['count'], textinfo='percent+value',
                  textposition='outside',
                  textfont=dict(color='white'))

fig.show()


# In[63]:


# df_new' is your DataFrame
df_sorted = df_new.sort_values(by='number_of_reviews', ascending=True)
top_N = 10
top_properties = df_sorted.head(top_N)

# Set a different template with a lighter background
fig = px.bar(top_properties, x='number_of_reviews', y='name', text='number_of_reviews',
             orientation='h', title=f'Top {top_N} Properties with Least Reviews)',
             labels={'number_of_reviews': 'Number of Reviews', 'name': 'Property Name'},
             template='plotly')  # Use the 'plotly' template for a lighter background

# Customize the appearance of the chart.
fig.update_traces(texttemplate='%{text} reviews', textposition='inside', textfont_size=14)
fig.update_layout(xaxis_title='Number of Reviews', yaxis_title='Property Name')

# Show the chart interactively.
fig.show()


# In[64]:


# Count the number of properties available for 60 days, 90 days, and 365 days
count_properties_below_30_days = df_new[df_new['availability_30'] < 30].shape[0]
count_properties_30_days = df_new[(df_new['availability_30'] >= 30) & (df_new['availability_30'] < 60)].shape[0]
count_properties_60_days = df_new[(df_new['availability_60'] >= 60) & (df_new['availability_60'] < 90)].shape[0]
count_properties_90_days = df_new[(df_new['availability_90'] >= 90) & (df_new['availability_90'] < 365)].shape[0]
count_properties_365_days = df_new[df_new['availability_365'] >= 365].shape[0]

# Create a bar chart
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the bars
bars = ax.bar(['below 30 Days', '30 Days', '60 Days', '90 Days', '365 Days'], [count_properties_below_30_days, count_properties_30_days, count_properties_60_days, count_properties_90_days, count_properties_365_days], color=['red', 'yellow','orange', 'green', 'blue'])

# Display the count values on top of the bars
for bar in bars:
    yval = bar.get_height()
    plt.annotate(str(int(yval)), xy=(bar.get_x() + bar.get_width() / 2, yval), xytext=(0, 3),
                 textcoords='offset points', ha='center', va='bottom', color='black')

ax.set_ylabel('Number of Properties')
ax.set_title('Number of Properties Available for Different Durations')

plt.show()


# In[65]:


# Convert 'suburb' column to string data type
df_new['suburb'] = df_new['suburb'].astype(str)

#Price Distribution by Suburb
fig = px.scatter(df_new, x='suburb', y='price', color='price', title='Price Distribution by Suburb',
                 color_continuous_scale='Viridis')  
fig.update_layout(xaxis_tickangle=-45)  
fig.show()


# In[66]:


# Aggregating data by suburb and calculating the mean price for each suburb
suburb_median_prices = df_new.groupby('country')['price'].mean().reset_index()

# Sorting the suburbs by median price in ascending order
suburb_median_prices = suburb_median_prices.sort_values(by='price')

# Define a custom color scale
colors = px.colors.sequential.Viridis

# Plotting with Plotly
fig = px.bar(suburb_median_prices, x='price', y='country', orientation='h',
             title='Mean Price by Country', labels={'price': 'Mean Price', 'country': 'Country'},
             color='price', color_continuous_scale=colors)
fig.update_layout(yaxis=dict(categoryorder='total ascending'), xaxis_title='Median Price')
fig.show()



# In[67]:


# Aggregating data by suburb and calculating the mean price for each suburb
suburb_median_prices = df_new.groupby('suburb')['price'].mean().reset_index()

# Sorting the suburbs by median price in descending order and selecting the top 10
suburb_median_prices = suburb_median_prices.sort_values(by='price', ascending=False).head(10)

plt.figure(figsize=(12, 6))
ax = sns.barplot(data=suburb_median_prices, x='price', y='suburb')
plt.xlabel('Average Price')
plt.ylabel('Suburbs')
plt.title('Top 10 Suburbs with the Highest Average Price')
plt.xticks(rotation=90)

# Add price annotations inside the bars
for p in ax.patches:
    ax.annotate(f"${p.get_width():.2f}", (p.get_width(), p.get_y() + p.get_height() / 2), ha='left', va='center')

plt.show()


# In[68]:


# Property type-based analysis with hover text
fig = px.scatter(df_new, x='property_type', y='price', text='price', color='price',
                 title='Price Distribution by Property Type', labels={'price': 'Price', 'property_type': 'Property Type'},
                 color_continuous_scale='Viridis')  # You can change 'Viridis' to any other Plotly color scale
fig.update_traces(textposition='top center')
fig.update_layout(
    xaxis_title='Property Type',
    yaxis_title='Price',
    title='Price Distribution by Property Type'
)
fig.update_xaxes(tickangle=45)
fig.show()



# In[69]:


# Group the data by 'country' and count the unique number of properties in each group
property_count_by_country = df_new.groupby('country')['name'].nunique().reset_index(name='property_count')

# Create an interactive bar chart with property count displayed inside the bar when hovering
fig = px.bar(property_count_by_country, x='country', y='property_count',
             labels={'country': 'Country', 'property_count': 'Property Count'},
             title='Number of Properties by Country',
             color='property_count',  # Use the 'property_count' column for color
             color_continuous_scale='Viridis')  # You can choose any other color scale

fig.update_traces(text=property_count_by_country['property_count'], textposition='inside')
fig.update_xaxes(categoryorder='total ascending')  # Sort bars by ascending property count

fig.show()


# In[70]:


# Group the data by 'country' and find the property with the highest price in each group
most_expensive_properties = df_new.groupby('country').apply(lambda x: x.loc[x['price'].idxmax()])

# Create a custom text column that includes both property name and price
most_expensive_properties['text'] = most_expensive_properties['name'] + ' - $' + most_expensive_properties['price'].astype(str)

# Create an interactive bar chart with property name and price displayed inside the bar when hovering
fig = px.bar(most_expensive_properties, x='country', y='price', text='text',
             labels={'country': 'Country', 'price': 'Price', 'text': 'Property Info'},
             title='Most Expensive Property by Country',
             color='price', color_continuous_scale='RdYlBu')

fig.update_traces(textposition='inside')
fig.update_xaxes(categoryorder='total ascending')  # Sort bars by ascending price

fig.show()



# In[71]:


import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import MarkerCluster

# Filter properties available for 365 days
properties_365_days = df_new[df_new['availability_365'] >= 365]

# Create a GeoDataFrame with latitude and longitude as geometry
geometry = [Point(xy) for xy in zip(properties_365_days['longitude'], properties_365_days['latitude'])]
geo_df = gpd.GeoDataFrame(properties_365_days, geometry=geometry)

# Create an interactive map centered around the median coordinates of the properties
center_lat, center_lon = geo_df['latitude'].median(), geo_df['longitude'].median()
mymap = folium.Map(location=[center_lat, center_lon], zoom_start=12)

# Add MarkerCluster to the map for better visualization of multiple markers
marker_cluster = MarkerCluster().add_to(mymap)

# Add markers for each property in the GeoDataFrame
for idx, row in geo_df.iterrows():
    folium.Marker(location=[row['latitude'], row['longitude']], popup=row['name']).add_to(marker_cluster)

# Display the interactive map
mymap


# In[ ]:


df_new.to_csv('airbnb.xlsx', index=False)


# In[ ]:


df_new['name'].nunique()

Key Insights:

1. Total Property Count: There are a total of 5,538 properties listed.
2. Popular Property Type: The most common property type is Apartments, with a significant count of        3,626 listings.
3. Variety of Property Types: There is a diversity of 36 unique property types available.
4. Highly Reviewed Property: The property named 'Waikiki Dream' stands out with 533 reviews, making it 5. one of the most reviewed properties. It is a private studio.
6. Review Status: Out of all properties, 4,167 have received reviews, while 1,388 have not yet            received any reviews.
7. Superhost Status: Among 5,104 hosts, only 1,090 hold the prestigious status of superhosts.
8. Host Response: A substantial number of hosts, specifically 2,175, respond to inquiries within an      hour.
8. Luxury Listing: The most expensive property is an apartment located in Turkey, priced at $48,842.
9. Price Range: The majority of properties (5,543) fall within the price range of $0 to $4,900.

These insights provide a comprehensive overview of the property listings, their popularity, review status, host attributes, and price distribution, offering valuable information for business analysis and decision-making processes.Recommendations:Based on the findings from the data analysis, some recommendations and insights can be suggested

	Focus on Apartment Listings: Since Apartments are the most common property type with a count of 3626, it's recommended to focus on optimizing listings, improving amenities, and enhancing customer experiences for this property type.
    
	Encourage Reviews: With 4167 properties having reviews and 1388 having no reviews, it's crucial to
encourage guests to leave reviews after their stay. Implementing strategies such as follow-up emails, incentives, or discounts for leaving reviews can help increase the number of reviews for properties.
    
	Superhost Recognition: Recognize and incentivize superhosts among the 1090 hosts who are superhosts out of 5104 hosts. Superhosts contribute significantly to the overall positive guest experience, and acknowledging their efforts can further improve guest satisfaction and loyalty.
    
	Improve Response Time: Since 2175 hosts usually respond within an hour, it's essential to maintain 
    or improve this response time. Prompt responses to guest inquiries and messages can lead to better
    guest experiences and higher booking rates.
    
	Optimize Pricing: Analyze and optimize pricing strategies, especially for properties priced between 0-4999. Ensure that pricing is competitive, reflects market demand, and offers value for money to guests.
    
	Enhance Marketing for 'Waikiki Dream': Promote the 'Waikiki Dream' property, which is the most reviewed property with 533 reviews. Highlight its unique features, amenities, and positive guest experiences in marketing campaigns to attract more bookings.
    
	Explore International Markets: Given that the most expensive property is in Turkey, priced at 48842,consider exploring opportunities in international markets. Targeting international travelers or 
expanding listings in popular international destinations can diversify revenue streams and attract a wider range of guests.
    
	Diversify Property Types: While Apartments are popular, consider diversifying the property types 
    offered to cater to different guest preferences. Including a variety of property types such as 
    houses, villas, cottages, etc., can attract a broader audience and meet diverse accommodation 
    needs.
    
By implementing these recommendations, property owners and Airbnb hosts can enhance their listings, 
improve guest experiences, and drive overall business growth and success.Limitations:
1. Data Completeness: Data or fields considered for analysis is solely based on the project requirement and Analyst's discretion

2. Data Quality: The quality of data in the Airbnb dataset can vary. Some listings may have inaccurate or  outdated information, such as incorrect property types, descriptions, or amenities. 

3. Sampling Bias: The Airbnb dataset may suffer from sampling bias, where certain types of properties, hosts, or regions are overrepresented or underrepresented.

4. Limited Geographic Coverage: The dataset may have limited geographic coverage, focusing on specific cities, countries, or regions. This limitation can restrict the applicability of insights to a wider geographical context.
    
5. Temporal Scope: The dataset may cover a specific time period, which could limit the analysis of trends over time
    
# In[ ]:




