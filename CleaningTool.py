import base64
import streamlit as st
import mysql.connector
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder
##from imblearn.over_sampling import RandomOverSampler, SMOTE
##from imblearn.under_sampling import RandomUnderSampler
##from sklearn.model_selection import train_test_split
##from sklearn.utils import resample



# Establish MySQL connection
mydb = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="disha13",
    database="CleaningTool"
)

# Function to create tables
def create_tables():
    cursor = mydb.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL
        )
    """)
    mydb.commit()

# Create tables if they don't exist
create_tables()

# Rest of your Streamlit code for registration and login goes here...
# Streamlit registration form
def register_user(username, email, password):
    cursor = mydb.cursor()
    sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    val = (username, email, password)
    cursor.execute(sql, val)
    mydb.commit()
    st.success("Registration Successful")

def login_user(username, password):
    cursor = mydb.cursor()
    sql = "SELECT * FROM users WHERE username = %s AND password = %s"
    val = (username, password)
    cursor.execute(sql, val)
    result = cursor.fetchone()

    if result:
        st.success("Login Successful")
    else:
        st.error("Invalid Credentials")

# Streamlit pages
# Streamlit pages
page = st.sidebar.radio("Navigation", ["Login", "Register"])

if page == "Login":
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login_user(username, password)

elif page == "Register":
    st.title("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        register_user(username, email, password)

def main():
    st.title('Data Cleaning Tool')

    # File upload
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

    if uploaded_file is not None:
        st.write("### Uploaded Dataset")
        df = pd.read_csv(uploaded_file)

        # Show the uploaded dataset
        st.write(df)

        # Column selection for data type change
        st.sidebar.title('Select Columns and Data Types')
        columns = df.columns.tolist()
        selected_columns = st.sidebar.multiselect('Select columns:', columns)

        data_types = {
            'int64': 'Integer',
            'float64': 'Float',
            'object': 'String',
            'datetime64': 'Datetime',
            'bool': 'Boolean',
            'category': 'Category'
        }

        data_type = st.sidebar.selectbox('Select data type:', options=list(data_types.keys()))

        if st.sidebar.button('Change Data Type'):
            if selected_columns:
                for col in selected_columns:
                    try:
                        df[col] = df[col].astype(data_type)
                        st.sidebar.success(f"Changed data type of '{col}' to '{data_types[data_type]}'")
                    except Exception as e:
                        st.sidebar.error(f"Error changing data type of '{col}': {e}")

            # Show updated DataFrame
            st.write("### Updated Dataset")
            st.write(df)
        
        # Handling missing values
        st.sidebar.title('Handle Missing Values')
        missing_values_action = st.sidebar.selectbox('Select action:', ('Drop missing values', 'Fill missing values'))

        if missing_values_action == 'Drop missing values':
            df.dropna(inplace=True)
            st.sidebar.success("Missing values dropped")
        elif missing_values_action == 'Fill missing values':
            fill_value = st.sidebar.text_input("Fill missing values with:")
            df.fillna(fill_value, inplace=True)
            st.sidebar.success(f"Filled missing values with '{fill_value}'")
        
         # Handling duplicates
        st.sidebar.title('Handle Duplicates')
        duplicate_action = st.sidebar.selectbox('Select action:', ('Show duplicates', 'Remove duplicates'))

        if duplicate_action == 'Show duplicates':
            duplicates = df[df.duplicated()]
            st.sidebar.write("### Duplicates Found")
            st.sidebar.write(duplicates)
        elif duplicate_action == 'Remove duplicates':
            df.drop_duplicates(inplace=True)
            st.sidebar.success("Duplicates removed")

        # Normalizing numeric columns
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        selected_numeric_columns = st.sidebar.multiselect('Select numeric columns to normalize:', numeric_columns)

        if st.sidebar.button('Normalize'):
            if selected_numeric_columns:
                scaler = MinMaxScaler()
                df[selected_numeric_columns] = scaler.fit_transform(df[selected_numeric_columns])
                st.sidebar.success("Selected numeric columns normalized")

        
        # Encoding categorical columns
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        selected_categorical_columns = st.sidebar.multiselect('Select categorical columns to encode:', categorical_columns)

        if st.sidebar.button('Encode Categorical'):
            if selected_categorical_columns:
                encoder = OneHotEncoder(sparse=False, drop='first')
                encoded_cols = pd.DataFrame(encoder.fit_transform(df[selected_categorical_columns]))
                encoded_cols.columns = encoder.get_feature_names(selected_categorical_columns)

                # Drop original categorical columns and concatenate encoded ones
                df = pd.concat([df.drop(selected_categorical_columns, axis=1), encoded_cols], axis=1)
                st.sidebar.success("Selected categorical columns encoded")
        
        # Drop irrelevant columns
        st.sidebar.title('Remove Irrelevant Columns')
        irrelevant_columns = st.sidebar.multiselect('Select columns to remove:', columns)
        
        if st.sidebar.button('Remove Columns'):
            if irrelevant_columns:
                df.drop(irrelevant_columns, axis=1, inplace=True)
                st.sidebar.success("Selected columns removed")
        # Show dataset after handling duplicates, normalization, encoding, and removing columns
        st.write("Cleaned Data")
        st.write(df)

        
def run():
    main()


if __name__ == "__main__":
    run()



