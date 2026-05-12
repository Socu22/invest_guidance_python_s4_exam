import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI server URL
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8080")

st.title("Streamlit CRUD Client for FastAPI")

# --- Function to fetch and display items ---
def refresh_items():
    try:
        response = requests.get(f"{FASTAPI_URL}/items")
        response.raise_for_status()
        items = response.json()
        if items:
            st.table(items)
        else:
            st.warning("No items found in the database.")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch items: {e}")

# --- READ ALL ITEMS (with refresh button) ---
st.header("View All Items")
refresh_items()  # Initial load

# --- CREATE NEW ITEM ---
st.header("Create New Item")
with st.form("create_item"):
    name = st.text_input("Name", key="create_name")
    description = st.text_input("Description", key="create_description")
    price = st.number_input("Price", min_value=0.0, key="create_price")
    submitted = st.form_submit_button("Create Item")

    if submitted:
        try:
            response = requests.post(
                f"{FASTAPI_URL}/items",
                json={"name": name, "description": description, "price": price}
            )
            response.raise_for_status()
            st.success(f"Item created: {response.json()}")
            st.rerun()  # Refresh the entire app
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to create item: {e}")

# --- UPDATE ITEM ---
st.header("Update Item")
item_id = st.number_input("Enter Item ID to Update", min_value=1, key="update_id")
try:
    response = requests.get(f"{FASTAPI_URL}/items/{item_id}")
    if response.status_code == 200:
        item = response.json()
        with st.form("update_item"):
            name = st.text_input("Name", value=item["name"], key="update_name")
            description = st.text_input("Description", value=item.get("description", ""), key="update_description")
            price = st.number_input("Price", value=item["price"], key="update_price")
            submitted = st.form_submit_button("Update Item")

            if submitted:
                try:
                    response = requests.put(
                        f"{FASTAPI_URL}/items/{item_id}",
                        json={"name": name, "description": description, "price": price}
                    )
                    response.raise_for_status()
                    st.success(f"Item updated: {response.json()}")
                    st.rerun()  # Refresh the entire app
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to update item: {e}")
    else:
        st.error("Item not found.")
except requests.exceptions.RequestException as e:
    st.error(f"Failed to fetch item: {e}")

# --- DELETE ITEM ---
st.header("Delete Item")
delete_id = st.number_input("Enter Item ID to Delete", min_value=1, key="delete_id")
if st.button("Delete Item"):
    try:
        response = requests.delete(f"{FASTAPI_URL}/items/{delete_id}")
        if response.status_code == 200:
            st.success(f"Item {delete_id} deleted successfully!")
            st.rerun()  # Refresh the entire app
        else:
            st.error(f"Failed to delete item: {response.json()}")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to delete item: {e}")