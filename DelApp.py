import streamlit as st
import pandas as pd
from io import BytesIO

# ---------------- Page Config ----------------
st.set_page_config(page_title="Delivered Orders App", layout="wide")
st.title("Delivered Orders Comparison")

# ---------------- File Upload ----------------
uploaded_file = st.file_uploader(
    "Upload Excel file",
    type=["xlsx"]
)

# ---------------- User Inputs ----------------
col1, col2 = st.columns(2)

with col1:
    old_dateNumber_of_days = st.number_input(
        "Old date (number of days ago)",
        min_value=0,
        value=14,
        step=1
    )

with col2:
    latest_day_number_of_days = st.number_input(
        "Latest date (number of days ago)",
        min_value=0,
        value=0,
        step=1
    )

# ---------------- Excel Helper ----------------
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# ---------------- Main Logic ----------------
if uploaded_file is not None:
    try:
        data = pd.read_excel(uploaded_file)

        # -------- Data Processing --------
        data["phone_number"] = data["phone_number"].astype(str)

        start_2 = data["phone_number"].str.startswith("2")
        data.loc[start_2, "phone_number"] = data.loc[start_2, "phone_number"].str[2:]

        data["order_code"] = "20" + data["phone_number"]

        data["customer_name"] = (
            data["customer_name"]
            .astype(str)
            .apply(lambda x: x.split(" ")[0])
        )

        data["delivery_status_date"] = pd.to_datetime(
            data["delivery_status_date"].astype(str).str[:10]
        )

        # -------- Date Calculation --------
        old_date = (
            pd.Timestamp.today().normalize()
            - pd.Timedelta(days=int(old_dateNumber_of_days))
        )

        latest_date = (
            pd.Timestamp.today().normalize()
            - pd.Timedelta(days=int(latest_day_number_of_days))
        )

        # -------- Final DataFrames (2 columns only) --------
        delivered_latest = (
            data.loc[data["delivery_status_date"] == latest_date,
                     ["order_code", "customer_name"]]
            .reset_index(drop=True)
        )

        delivered_old = (
            data.loc[data["delivery_status_date"] == old_date,
                     ["order_code", "customer_name"]]
            .reset_index(drop=True)
        )

        # ---------------- Display ----------------
        st.subheader(f"Delivered on {latest_date.date()}")
        st.dataframe(delivered_latest, use_container_width=True)

        st.subheader(f"Delivered on {old_date.date()}")
        st.dataframe(delivered_old, use_container_width=True)

        # ---------------- Download ----------------
        st.download_button(
            "Download Latest Delivered (Excel)",
            data=to_excel(delivered_latest),
            file_name="delivered_latest.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.download_button(
            "Download Old Delivered (Excel)",
            data=to_excel(delivered_old),
            file_name="delivered_old.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("من فضلك ارفع ملف Excel عشان نبدأ")
