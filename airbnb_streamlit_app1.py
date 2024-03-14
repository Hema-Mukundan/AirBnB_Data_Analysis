import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# Load Airbnb dataset
airbnb_data = pd.read_csv('C:\\Users\\Raghu\\OneDrive\\Desktop\\Capstone_Projects\\AirBnB_Project\\airbnb.csv')

st.title("Airbnb Data Analysis")

# Sidebar options
analysis_option = st.sidebar.selectbox("Select Analysis", ["Property Listings", "Price Analysis", "Availability Analysis"])

# Geospatial Visualization
if analysis_option == "Property Listings":
        st.subheader("Listing of selected Property")

        # Sidebar options for filtering
        selected_country = st.sidebar.selectbox("Select Country", airbnb_data['country'].unique())
        selected_suburb = st.sidebar.selectbox("Select Suburb", airbnb_data[airbnb_data['country'] == selected_country]['suburb'].unique())
        selected_property_type = st.sidebar.selectbox("Select Property Type", airbnb_data[(airbnb_data['country'] == selected_country) & (airbnb_data['suburb'] == selected_suburb)]['property_type'].unique())

        # Filter data by selected options
        filtered_data = airbnb_data[(airbnb_data['country'] == selected_country) & (airbnb_data['suburb'] == selected_suburb) & (airbnb_data['property_type'] == selected_property_type)]

        # Create Folium map
        m = folium.Map(location=[filtered_data['latitude'].mean(), filtered_data['longitude'].mean()], zoom_start=12)

        # Add markers for each property to map
        for index, row in filtered_data.iterrows():
            folium.Marker([row['latitude'], row['longitude']], popup=row['name']).add_to(m)

        # Display the map
        folium_static(m)

# Price Analysis
elif analysis_option == "Price Analysis":
    st.subheader("Price Analysis")

    # Summary statistics
    st.write("Summary Statistics of Property Price")
    summary_table = airbnb_data['price'].describe().to_frame()
    summary_table_html = summary_table.to_html()
    styled_summary_table_html = (
        summary_table_html
        .replace('<table border="1" class="dataframe">', '<table style="border-collapse: collapse; width: 100%;">')
        .replace('<th>', '<th style="background-color: #f2f2f2; color: black; text-align: left;">')
        .replace('<td>', '<td style="text-align: left;">')
        .replace('<tr style="text-align: right;">', '<tr>')
        .replace('<tr>', '<tr onmouseover="this.style.backgroundColor=\'#ffffb3\';" onmouseout="this.style.backgroundColor=\'\';">')
    )
    st.write(styled_summary_table_html, unsafe_allow_html=True)


    # Distribution plot
    st.write("Distribution of Prices:")
    fig = px.histogram(airbnb_data, x='price', nbins=20, histfunc='count', 
                    title='Distribution of Prices')
    fig.update_layout(xaxis_title='Price', yaxis_title='Count')
    st.plotly_chart(fig, use_container_width=True)


    # Price by property type
    st.write("Average Price of Property Type by Suburb:")
    price_by_property_type = airbnb_data.groupby('property_type')['price'].mean()
    
    st.bar_chart(price_by_property_type)

    fig = px.scatter(airbnb_data, x='property_type', y='price', color='price', title='Price Distribution by Property Type',
                    color_continuous_scale='Viridis')  
    fig.update_layout(xaxis_tickangle=-45)  

    # Display the plot using Streamlit
    st.plotly_chart(fig)


    # Average price by Suburb
    st.write("Average Price by Suburb")

    # Aggregating data by suburb and calculating the average price for each suburb
    suburb_average_prices = airbnb_data.groupby('suburb')['price'].mean().reset_index()

    # Sorting the suburbs by average price in ascending order
    suburb_average_prices = suburb_average_prices.sort_values(by='price')

    # Define a custom color scale
    colors = px.colors.sequential.Viridis

    # Plotting with Plotly
    fig = px.bar(suburb_average_prices, x='price', y='suburb', orientation='h',
                title='Average Price by Suburb', labels={'price': 'Average Price', 'suburb': 'Suburb'},
                color='price', color_continuous_scale=colors)
    fig.update_layout(yaxis=dict(categoryorder='total ascending'), xaxis_title='Average Price')


    
# Availability Analysis
if analysis_option == "Availability Analysis":
    #st.subheader("Availability Analysis")

    # Count the number of properties available for 30 days, 60 days, 90 days, and 365 days
    count_properties_30_days = airbnb_data[airbnb_data['availability_30'] >= 30].shape[0]
    count_properties_60_days = airbnb_data[airbnb_data['availability_365'] >= 60].shape[0]
    count_properties_90_days = airbnb_data[airbnb_data['availability_365'] >= 90].shape[0]
    count_properties_365_days = airbnb_data[airbnb_data['availability_365'] >= 365].shape[0]

    # Create a bar chart
    st.subheader("Number of Properties Available for Different Durations")
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot the bars
    bars = ax.bar(['30 Days', '60 Days', '90 Days', '365 Days'], 
                [count_properties_30_days, count_properties_60_days, count_properties_90_days, count_properties_365_days], 
                color=['red', 'orange', 'green', 'blue'])

    # Display the count values on top of the bars
    for bar in bars:
        yval = bar.get_height()
        plt.annotate(str(int(yval)), xy=(bar.get_x() + bar.get_width() / 2, yval), xytext=(0, 3),
                    textcoords='offset points', ha='center', va='bottom', color='black')

    ax.set_ylabel('Number of Properties')
    ax.set_title('Number of Properties Available for Different Durations')

    # Display the plot using Streamlit
    st.pyplot(fig)


    #Check availability of property with price/night
    # Dropdown menu to select property name
    selected_property = st.selectbox("Select Property to check availability", airbnb_data['name'].unique())

    # Filter data for the selected property
    selected_property_data = airbnb_data[airbnb_data['name'] == selected_property]

    # Display the images of the selected property
    selected_property_images = selected_property_data['images'].values
    if len(selected_property_images) > 0:
        for image_path in selected_property_images:
            st.image(image_path, caption="Image of the selected property", width=200)
    else:
        st.write("No images available for the selected property")



    # Calculate total availability for the selected property
    total_availability = selected_property_data[['availability_30', 'availability_60', 'availability_90', 'availability_365']].sum().sum()

    # Display the total availability
    st.markdown(f"**Availability of Property '{selected_property}**': {total_availability} days")

    ## Display the filtered data
    prices_rounded = [f"${price:.2f} per night" for price in selected_property_data['price'].values]
    price_info = ", ".join(prices_rounded)
    st.markdown(f"**Price Information for Selected Property:** {price_info}")



