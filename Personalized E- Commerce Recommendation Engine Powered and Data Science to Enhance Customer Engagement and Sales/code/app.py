import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import TruncatedSVD

st.set_page_config(page_title="Product Recommendation System", layout="wide")
st.title("🛍️ Personalized E-Commerce Recommendation Engine")

# Upload CSV
uploaded_file = st.file_uploader("Upload 'customers_rating.csv'", type=["csv"])

if uploaded_file:
    amazon_ratings = pd.read_csv(uploaded_file)
    st.subheader("📊 Dataset Preview")
    st.dataframe(amazon_ratings.head())

    st.markdown("### 👥 Dataset Info")
    st.write(f"Total entries: {amazon_ratings.shape[0]}")
    st.write(f"Unique Users: {amazon_ratings['UserId'].nunique()}")
    st.write(f"Unique Products: {amazon_ratings['ProductId'].nunique()}")

    st.markdown("## 🔥 Most Popular Products (New User Recommendation)")
    popular_products = pd.DataFrame(amazon_ratings.groupby('ProductId')['Rating'].count())
    most_popular = popular_products.sort_values('Rating', ascending=False)
    st.write("Top 10 Most Popular Products:")
    st.dataframe(most_popular.head(10))

    st.bar_chart(most_popular.head(30))

    st.markdown("## 🤝 Personalized Recommendations (Existing User)")
    amazon_ratings_subset = amazon_ratings.head(20000)

    ratings_matrix = amazon_ratings_subset.pivot_table(values='Rating', index='UserId', columns='ProductId', fill_value=0)

    # Transpose the matrix
    X = ratings_matrix.T

    # SVD decomposition
    SVD = TruncatedSVD(n_components=10)
    decomposed_matrix = SVD.fit_transform(X)

    # Correlation matrix
    correlation_matrix = np.corrcoef(decomposed_matrix)

    product_names = list(X.index)

    # Select a product for recommendation
    selected_product = st.selectbox("Select a Product ID to Get Recommendations", product_names)

    if selected_product:
        product_index = product_names.index(selected_product)
        correlation_product_ID = correlation_matrix[product_index]

        Recommend_list = list(X.index[correlation_product_ID > 0.90])
        if selected_product in Recommend_list:
            Recommend_list.remove(selected_product)

        st.markdown("### 🧠 Top 10 Recommended Products Based on User Purchase Similarity")
        if Recommend_list:
            st.write(Recommend_list[:10])
        else:
            st.warning("No strong recommendations found for this product.")
