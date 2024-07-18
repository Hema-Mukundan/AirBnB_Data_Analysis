import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.figure_factory as ff
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# Load Airbnb dataset
airbnb_data = pd.read_csv('C:\\Users\\Raghu\\OneDrive\\Desktop\\Capstone_Projects\\AirBnB_Project\\airbnb.csv')

st.title("Airbnb Data Analysis")

# Sidebar options
analysis_option = st.sidebar.selectbox("Select Analysis", ["Property Listings", "Price Analysis", "Availability Analysis", "Host Analysis"])

# Geospatial Visualization
if analysis_option == "Property Listings":
        st.subheader("Property Listings based on your selection")
 
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

        # Display the total number of properties
        total_properties = len(filtered_data)
        st.write(f"**Number of properties available for your selected criteria: {total_properties}**")

        # Display top 5 properties based on selection
        # st.subheader("Top 5 Properties")
        
        # Sort filtered data by some relevant criteria (e.g., price, rating, etc.) and get top 5
        top_5_properties = filtered_data.sort_values(by='number_of_reviews', ascending=False).head(5)  # Example: sorting by price

        # Display top 5 properties based on number_of_reviews
        st.subheader(f"Top 5 Properties in {selected_suburb}, {selected_country} - {selected_property_type} by Number of Reviews")
        if not top_5_properties.empty:
            st.write(top_5_properties[['name', 'price', 'number_of_reviews', 'property_type']].reset_index(drop=True))
        else:
            st.write("No properties found matching the selected criteria.")

# Price Analysis
elif analysis_option == "Price Analysis":
    st.subheader("Price Analysis")

    # Filter options
    filter_option = st.sidebar.radio("Filter by", ["Overall", "Country-wise", "Suburb-wise"])

    if filter_option == "Overall":
        st.markdown("<h2 style='text-align: center;'>Summary Statistics of Property Price</h2>", unsafe_allow_html=True)
        summary_stats = airbnb_data['price'].describe()
        
        # Display summary statistics in individual boxes with CSS for styling
        col1, col2, col3, col4 = st.columns(4)

        # Define CSS for square box styling
        box_style = "border: 5px solid #ddd; padding: 10px; border-radius: 5px; height: 75px; text-align: center; display: flex; justify-content: center; align-items: center; flex-direction: column;" 

        with col1:
            st.markdown(f'<div style="{box_style} background-color: #afeeee;"><span style="font-weight: bold;">Min Price</span><br><span style="font-weight: bold;">${summary_stats["min"]:.2f}</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div style="{box_style} background-color: #b0e57c;"><span style="font-weight: bold;">Median Price</span><br><span style="font-weight: bold;">${summary_stats["50%"]:.2f}</span></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div style="{box_style} background-color: #ffcccb;"><span style="font-weight: bold;">Mean Price</span><br><span style="font-weight: bold;">${summary_stats["mean"]:.2f}</span></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div style="{box_style} background-color: #f0e68c;"><span style="font-weight: bold;">Max Price</span><br><span style="font-weight: bold;">${summary_stats["max"]:.2f}</span></div>', unsafe_allow_html=True)
        
        # Distribution plot (Histogram) for property prices
        fig_hist = px.histogram(airbnb_data, x='price', nbins=20, title='Overall Price Distribution of Properties')
        fig_hist.update_layout(xaxis_title='Price', yaxis_title='Count')
        st.plotly_chart(fig_hist, use_container_width=True)

        # Price by property type
        price_by_property_type = airbnb_data.groupby('property_type')['price'].mean()
        fig = px.scatter(airbnb_data, x='property_type', y='price', color='price', title='Overall Price Distribution by Property Type',
                        color_continuous_scale='Viridis')  
        fig.update_layout(xaxis_tickangle=-45)  
        st.plotly_chart(fig)

    elif filter_option == "Country-wise":
        countries = airbnb_data['country'].unique()
        selected_country = st.sidebar.selectbox("Select Country", countries)

        # st.write(f"Price Distribution of Properties in {selected_country}")
        filtered_data = airbnb_data[airbnb_data['country'] == selected_country]
        fig_country = px.histogram(filtered_data, x='price', nbins=20, title=f"Price Distribution in {selected_country}")
        fig_country.update_layout(xaxis_title='Price', yaxis_title='Count')
        st.plotly_chart(fig_country, use_container_width=True)

    elif filter_option == "Suburb-wise":
        suburbs = airbnb_data['suburb'].unique()
        selected_suburb = st.sidebar.selectbox("Select Suburb", suburbs)

        # st.write(f"Price Distribution of Properties in {selected_suburb}")
        filtered_data = airbnb_data[airbnb_data['suburb'] == selected_suburb]
        fig_suburb = px.histogram(filtered_data, x='price', nbins=20, title=f"Price Distribution in {selected_suburb}")
        fig_suburb.update_layout(xaxis_title='Price', yaxis_title='Count')
        st.plotly_chart(fig_suburb, use_container_width=True)

    # # Aggregating data by suburb and calculating the average price for each suburb
    # suburb_average_prices = airbnb_data.groupby('suburb')['price'].mean().reset_index()

    # # Sorting the suburbs by average price in ascending order
    # suburb_average_prices = suburb_average_prices.sort_values(by='price')

    # # Define a custom color scale
    # colors = px.colors.sequential.Viridis

    # # Plotting with Plotly
    # fig = px.bar(suburb_average_prices, x='price', y='suburb', orientation='h',
    #             title='Average Price by Suburb', labels={'price': 'Average Price', 'suburb': 'Suburb'},
    #             color='price', color_continuous_scale=colors)
    # fig.update_layout(yaxis=dict(categoryorder='total ascending'), xaxis_title='Average Price')
  
# Availability Analysis
elif analysis_option == "Availability Analysis":
    #st.subheader("Availability Analysis")

    # Radio buttons to choose between Availability stats and Check Availability
    availability_option = st.sidebar.radio("Choose an option", ["Availability stats", "Check Availability"])

    if availability_option == "Availability stats":
        # Calculate the number of properties available for different durations
        count_properties_below_30_days = airbnb_data[airbnb_data['availability_365'] < 30].shape[0]
        count_properties_30_days = airbnb_data[(airbnb_data['availability_365'] >= 30) & (airbnb_data['availability_365'] < 60)].shape[0]
        count_properties_60_days = airbnb_data[(airbnb_data['availability_365'] >= 60) & (airbnb_data['availability_365'] < 90)].shape[0]
        count_properties_90_days = airbnb_data[(airbnb_data['availability_365'] >= 90) & (airbnb_data['availability_365'] < 365)].shape[0]
        count_properties_365_days = airbnb_data[airbnb_data['availability_365'] >= 365].shape[0]

        # Data for plotting
        data = {
            'Category': ['below 30 Days', '30 Days', '60 Days', '90 Days', '365 Days'],
            'Count': [count_properties_below_30_days, count_properties_30_days, count_properties_60_days, count_properties_90_days, count_properties_365_days]
        }

        # Create a DataFrame
        df_plot = pd.DataFrame(data)

        # Create an interactive bar chart using Plotly
        fig = px.bar(df_plot, x='Category', y='Count', color='Category', title='Number of Properties Available for Different Durations')

        # Display the plot in Streamlit
        st.plotly_chart(fig)
        
    elif availability_option == "Check Availability":
        # Dropdown menu to select country, suburb, and property name
        col1, col2 = st.columns(2)
        with col1:
            selected_country = st.selectbox("Select Country", airbnb_data['country'].unique())
        with col2:
            selected_suburb = st.selectbox("Select Suburb", airbnb_data[airbnb_data['country'] == selected_country]['suburb'].unique())

        selected_property = st.selectbox("Select Property to check availability", airbnb_data[(airbnb_data['country'] == selected_country) & (airbnb_data['suburb'] == selected_suburb)]['name'].unique())

        # #Check availability of property with price/night
        # # Dropdown menu to select property name
        # selected_property = st.selectbox("Select Property to check availability", airbnb_data['name'].unique())

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

# Host Analysis
elif analysis_option == "Host Analysis":
    st.header("Host Analysis")

    # Sidebar radio buttons for host analysis options
    host_analysis_option = st.sidebar.radio(
        "Select Host Analysis Option",
        ("Super Host", "Host Identity Verified", "Host Response Time")
    )

    if host_analysis_option == "Super Host":
        if 'host_is_superhost' in airbnb_data.columns:
            # Calculate the counts of superhost and non-superhost
            superhost_counts = airbnb_data['host_is_superhost'].value_counts()

            # Create a Host Superhost Status Pie Chart
            fig = px.pie(superhost_counts, names=superhost_counts.index, values=superhost_counts.values, title="Host Superhost Status", color_discrete_sequence=['lightblue', 'red'])

            # Display the chart
            st.plotly_chart(fig)
        else:
            st.error("The column 'host_is_superhost' does not exist in the dataset.")

    elif host_analysis_option == "Host Identity Verified":
        if 'host_identity_verified' in airbnb_data.columns:
            # Calculate the counts of verified and non-verified hosts
            host_verified_counts = airbnb_data['host_identity_verified'].value_counts()

            # Create a Host Verified Status Pie Chart
            fig = px.pie(host_verified_counts, names=host_verified_counts.index, values=host_verified_counts.values, title="Host Verified Status", color_discrete_sequence=['lightgreen', 'purple'])

            # Display the chart
            st.plotly_chart(fig)
        else:
            st.error("The column 'host_identity_verified' does not exist in the dataset.")

    elif host_analysis_option == "Host Response Time":
        if 'host_response_time' in airbnb_data.columns:
            # Group by 'host_response_time' and calculate the count
            host_response_time_counts = airbnb_data['host_response_time'].value_counts().reset_index(name='count')
            host_response_time_counts.columns = ['host_response_time', 'count']

            # Create the pie chart
            fig = px.pie(host_response_time_counts, names='host_response_time', values='count', hole=0.5, title="Host Response Time",
                         color_discrete_sequence=px.colors.qualitative.Set1)

            fig.update_traces(text=host_response_time_counts['count'], textinfo='percent+value',
                              textposition='outside',
                              textfont=dict(color='white'))

            # Display the chart
            st.plotly_chart(fig)
        else:
            st.error("The column 'host_response_time' does not exist in the dataset.")

   





