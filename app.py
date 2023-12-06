import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import numpy as np

# Load the dataset (replace 'videogame_sales.csv' with your dataset file path)
@st.cache_data
def load_data():
    data = pd.read_csv('vgsales.csv')
    return data

# Main function to create the Streamlit app
def main():
    st.title("Video Game Sales Analysis\n Sales in millions")
    st.sidebar.title("Select Options")

    data = load_data()
    data.drop(columns=['Name', 'Rank'], inplace=True)

    # Fill null/Nan values in 'Year' with the mean of existing years (rounded to nearest year)
    mean_year = round(data['Year'].mean())
    data['Year'].fillna(mean_year, inplace=True)

    # Categorize publishers with less than 50 games as "Small Publishers"
    publisher_counts = data['Publisher'].value_counts()
    small_publishers = publisher_counts[publisher_counts < 50].index
    data.loc[data['Publisher'].isin(small_publishers), 'Publisher'] = 'Small Publisher'

    # Sidebar: Select columns for analysis
    selected_x_column = st.sidebar.selectbox(
        "Select X-Axis Column",
        ["Publisher", "Platform", "Genre", 'Year']
    )

    selected_y_column = st.sidebar.selectbox(
        "Select Y-Axis Column",
        ["Global_Sales_in_Millions", "NA_Sales_in_Million", "EU_Sales_in_Millions", "JP_Sales_in_Millions", "Other_Sales_in_Millions"]
    )

    # Filter data based on selected columns
    filtered_data = data[[selected_x_column, selected_y_column]]

    # Group the data by the selected x-axis column and sum the y-axis column
    grouped_data = filtered_data.groupby(selected_x_column)[selected_y_column].sum().reset_index()

    # Display the bar graph
    st.subheader(f"Bar Graph: {selected_y_column} by {selected_x_column}")
    plt.figure(figsize=(12, 6))
    plt.bar(grouped_data[selected_x_column], grouped_data[selected_y_column])
    plt.xlabel(selected_x_column)
    plt.ylabel(selected_y_column)
    plt.xticks(rotation=45, ha="right")
    st.pyplot(plt)

    # Polynomial Regression for Sales Prediction
    if selected_x_column == 'Year':
        st.sidebar.subheader("Sales Prediction")
        selected_genre = st.sidebar.selectbox("Select Genre", data['Genre'].unique())
        selected_start_year = st.sidebar.slider("Select Start Year for Prediction", int(data['Year'].min()), int(data['Year'].max()))
        selected_end_year = st.sidebar.number_input("Select End Year for Prediction", int(data['Year'].min()), 3000, value=3000)

        st.write(f"Predicting {selected_y_column} for {selected_genre} games from {selected_start_year} to {selected_end_year}")

        # Filter data for the selected genre
        genre_data = data[data['Genre'] == selected_genre]

        # Prepare data for polynomial regression
        X = genre_data['Year'].values.reshape(-1, 1)
        y = genre_data[selected_y_column].values

        # Create polynomial features
        polynomial_degree = 2  # You can adjust the degree as needed
        poly = PolynomialFeatures(degree=polynomial_degree)
        X_poly = poly.fit_transform(X)

        # Create and fit the polynomial regression model
        model = LinearRegression()
        model.fit(X_poly, y)

        # Predict global sales for the selected year range
        years_to_predict = np.arange(selected_start_year, selected_end_year + 1).reshape(-1, 1)
        years_to_predict_poly = poly.transform(years_to_predict)
        predicted_sales = model.predict(years_to_predict_poly)

        # Plot the polynomial regression curve
        plt.figure(figsize=(12, 6))
        plt.scatter(X, y, color='blue', label='Actual Data')
        plt.plot(years_to_predict, predicted_sales, color='red', label='Polynomial Regression')
        plt.xlabel("Year")
        plt.ylabel(selected_y_column)
        plt.legend()
        st.pyplot(plt)

        # Output the predicted global sales for the selected year
        selected_year = st.sidebar.number_input("Select a Year to Get Predicted Global Sales", selected_start_year, selected_end_year, selected_end_year)
        selected_year_poly = poly.transform(np.array([[selected_year]]))
        predicted_global_sales = model.predict(selected_year_poly)[0]

        st.write(f"Predicted Global Sales for {selected_genre} games in {selected_year}: {predicted_global_sales:.2f} million units")

if __name__ == "__main__":
    main()
