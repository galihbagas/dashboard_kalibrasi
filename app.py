
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import calendar

import calendar

st.set_page_config(
    page_title="Dashboard Kalibrasi",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ Dashboard Kalibrasi")
st.caption("Sistem Monitoring Alat Ukur dan Jadwal Kalibrasi")

# Data awal
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {
            "No": "CAL-001",
            "Nama Alat": "Digital Caliper",
            "Merk": "Mitutoyo",
            "Lokasi": "QC",
            "Tanggal Kalibrasi": date.today(),
            "Interval (bulan)": 12,
            "Status": "Aktif"
        },
        {
            "No": "CAL-002",
            "Nama Alat": "Micrometer",
            "Merk": "Mitutoyo",
            "Lokasi": "Produksi",
            "Tanggal Kalibrasi": date.today() - timedelta(days=350),
            "Interval (bulan)": 12,
            "Status": "Aktif"
        }
    ])

df = st.session_state.data.copy()

# Hitung jatuh tempo
df["Jatuh Tempo"] = df.apply(
    lambda row: row["Tanggal Kalibrasi"] +
    pd.DateOffset(months=int(row["Interval (bulan)"])),
    axis=1
)

df["Sisa Hari"] = (
    pd.to_datetime(df["Jatuh Tempo"]) -
    pd.Timestamp(date.today())
).dt.days

df["Status Kalibrasi"] = df["Sisa Hari"].apply(
    lambda x: "Expired" if x < 0
    else "Segera" if x <= 30
    else "Valid"
)

# Dashboard summary
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Alat", len(df))
c2.metric("Kalibrasi Valid", len(df[df["Status Kalibrasi"] == "Valid"]))
c3.metric("Segera Jatuh Tempo", len(df[df["Status Kalibrasi"] == "Segera"]))
c4.metric("Expired", len(df[df["Status Kalibrasi"] == "Expired"]))

st.divider()

# Menu
menu = st.sidebar.selectbox(
    "Menu Dashboard",
    [
        "Dashboard",
        "Data Alat Ukur",
        "Tambah Alat",
        "Export Excel"
    ]
)

if menu == "Dashboard":
    st.subheader("Monitoring Kalibrasi")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Reminder Kalibrasi")

    reminder = df[df["Sisa Hari"] <= 30]

    if len(reminder) > 0:
        st.warning("Ada alat yang segera jatuh tempo atau expired.")
        st.dataframe(reminder, use_container_width=True)
    else:
        st.success("Tidak ada kalibrasi yang jatuh tempo.")

elif menu == "Data Alat Ukur":
    st.subheader("Data Alat Ukur")
    st.dataframe(df, use_container_width=True)

elif menu == "Tambah Alat":
    st.subheader("Tambah Data Alat")

    with st.form("form_alat"):
        nomor = st.text_input("Nomor alat")
        nama = st.text_input("Nama alat")
        merk = st.text_input("Merk")
        lokasi = st.text_input("Lokasi")
        tanggal = st.date_input("Tanggal kalibrasi")
        interval = st.number_input(
            "Interval kalibrasi (bulan)",
            min_value=1,
            value=12
        )

        submit = st.form_submit_button("Simpan Alat")

        if submit:
            if nomor and nama:
                new_data = {
                    "No": nomor,
                    "Nama Alat": nama,
                    "Merk": merk,
                    "Lokasi": lokasi,
                    "Tanggal Kalibrasi": tanggal,
                    "Interval (bulan)": interval,
                    "Status": "Aktif"
                }

                st.session_state.data = pd.concat(
                    [
                        st.session_state.data,
                        pd.DataFrame([new_data])
                    ],
                    ignore_index=True
                )

                st.success("Data alat berhasil ditambahkan.")
            else:
                st.error("Nomor dan nama alat wajib diisi.")

elif menu == "Export Excel":
    st.subheader("Export Data Kalibrasi")

    excel_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Data CSV",
        data=excel_data,
        file_name="data_kalibrasi.csv",
        mime="text/csv"
    )
