
import streamlit as st
import pandas as pd
from datetime import date
from calendar import monthrange
from io import BytesIO

st.set_page_config(
    page_title="Dashboard Kalibrasi",
    page_icon="🔧",
    layout="wide"
)

# ================= LOGIN =================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Login Dashboard Kalibrasi")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        masuk = st.form_submit_button("Login")

    if masuk:
        if username == "admin" and password == "kalibrasi123":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Username atau password salah")

    st.stop()

# ================= DATA =================
kolom = [
    "ID Alat",
    "Nama Alat",
    "Merk",
    "Lokasi",
    "Tanggal Kalibrasi",
    "Interval (Bulan)"
]

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {
            "ID Alat": "CAL-001",
            "Nama Alat": "Digital Caliper",
            "Merk": "Mitutoyo",
            "Lokasi": "QC",
            "Tanggal Kalibrasi": date.today(),
            "Interval (Bulan)": 12
        },
        {
            "ID Alat": "CAL-002",
            "Nama Alat": "Micrometer",
            "Merk": "Mitutoyo",
            "Lokasi": "Produksi",
            "Tanggal Kalibrasi": date.today(),
            "Interval (Bulan)": 12
        }
    ], columns=kolom)

if "sertifikat" not in st.session_state:
    st.session_state.sertifikat = {}

if "riwayat" not in st.session_state:
    st.session_state.riwayat = []

# ================= FUNGSI =================
def tambah_bulan(tanggal, bulan):
    bulan_total = tanggal.month - 1 + int(bulan)
    tahun = tanggal.year + bulan_total // 12
    bulan_baru = bulan_total % 12 + 1
    hari = min(tanggal.day, monthrange(tahun, bulan_baru)[1])

    return date(tahun, bulan_baru, hari)

def tanggal_jatuh_tempo(row):
    tanggal = pd.to_datetime(
        row["Tanggal Kalibrasi"]
    ).date()

    return tambah_bulan(
        tanggal,
        row["Interval (Bulan)"]
    )

def status_alat(row):
    jatuh_tempo = tanggal_jatuh_tempo(row)
    sisa = (jatuh_tempo - date.today()).days

    if sisa < 0:
        return "Expired"
    elif sisa <= 30:
        return "Segera Kalibrasi"
    else:
        return "Valid"

def format_data(df):
    hasil = df.copy()

    hasil["Tanggal Kalibrasi"] = pd.to_datetime(
        hasil["Tanggal Kalibrasi"]
    ).dt.date

    hasil["Jatuh Tempo"] = hasil.apply(
        tanggal_jatuh_tempo,
        axis=1
    )

    hasil["Status"] = hasil.apply(
        status_alat,
        axis=1
    )

    return hasil

# ================= SIDEBAR =================
st.sidebar.title("🔧 Kalibrasi")

menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Data Alat",
        "Tambah Alat",
        "Upload Sertifikat",
        "Riwayat Kalibrasi",
        "Export Excel"
    ]
)

if st.sidebar.button("Logout"):
    st.session_state.login = False
    st.rerun()

df = st.session_state.data.copy()
df_status = format_data(df)

# ================= DASHBOARD =================
if menu == "Dashboard":
    st.title("📊 Dashboard Kalibrasi")

    total = len(df_status)
    valid = len(df_status[df_status["Status"] == "Valid"])
    segera = len(
        df_status[df_status["Status"] == "Segera Kalibrasi"]
    )
    expired = len(
        df_status[df_status["Status"] == "Expired"]
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Alat", total)
    c2.metric("Valid", valid)
    c3.metric("Segera Kalibrasi", segera)
    c4.metric("Expired", expired)

    st.subheader("📋 Status Alat")

    st.dataframe(
        df_status,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("⚠️ Reminder Kalibrasi")

    reminder = df_status[
        df_status["Status"] != "Valid"
    ]

    if len(reminder) > 0:
        st.warning(
            "Ada alat yang perlu segera dikalibrasi."
        )

        st.dataframe(
            reminder,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("Semua alat masih valid.")

# ================= DATA ALAT =================
elif menu == "Data Alat":
    st.title("📋 Data Alat Ukur")

    st.dataframe(
        df_status,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Hapus Alat")

    if len(df) > 0:
        pilihan = st.selectbox(
            "Pilih ID alat",
            df["ID Alat"].tolist()
        )

        if st.button("Hapus Alat"):
            st.session_state.data = df[
                df["ID Alat"] != pilihan
            ].reset_index(drop=True)

            st.session_state.sertifikat.pop(
                pilihan,
                None
            )

            st.success("Alat berhasil dihapus")
            st.rerun()

# ================= TAMBAH ALAT =================
elif menu == "Tambah Alat":
    st.title("➕ Tambah Alat Ukur")

    with st.form("form_alat"):
        id_alat = st.text_input("ID Alat")
        nama = st.text_input("Nama Alat")
        merk = st.text_input("Merk")
        lokasi = st.text_input("Lokasi")
        tanggal = st.date_input(
            "Tanggal Kalibrasi",
            value=date.today()
        )
        interval = st.number_input(
            "Interval Kalibrasi (Bulan)",
            min_value=1,
            max_value=120,
            value=12
        )

        simpan = st.form_submit_button("Simpan Alat")

    if simpan:
        if not id_alat or not nama:
            st.error("ID alat dan nama alat wajib diisi")

        elif id_alat in df["ID Alat"].values:
            st.error("ID alat sudah terdaftar")

        else:
            data_baru = pd.DataFrame([{
                "ID Alat": id_alat,
                "Nama Alat": nama,
                "Merk": merk,
                "Lokasi": lokasi,
                "Tanggal Kalibrasi": tanggal,
                "Interval (Bulan)": interval
            }])

            st.session_state.data = pd.concat(
                [df, data_baru],
                ignore_index=True
            )

            st.session_state.riwayat.append({
                "ID Alat": id_alat,
                "Nama Alat": nama,
                "Tanggal": tanggal,
                "Keterangan": "Alat ditambahkan"
            })

            st.success("Alat berhasil ditambahkan")
            st.rerun()

# ================= SERTIFIKAT =================
elif menu == "Upload Sertifikat":
    st.title("📄 Upload Sertifikat Kalibrasi")

    if len(df) == 0:
        st.warning("Belum ada alat terdaftar")
    else:
        id_pilih = st.selectbox(
            "Pilih ID Alat",
            df["ID Alat"].tolist()
        )

        file = st.file_uploader(
            "Upload sertifikat PDF",
            type=["pdf"]
        )

        if file is not None:
            st.session_state.sertifikat[id_pilih] = {
                "nama": file.name,
                "data": file.getvalue()
            }

            st.success("Sertifikat berhasil diupload")

        sertifikat = st.session_state.sertifikat.get(
            id_pilih
        )

        if sertifikat:
            st.write("Sertifikat:", sertifikat["nama"])

            st.download_button(
                "Download Sertifikat",
                data=sertifikat["data"],
                file_name=sertifikat["nama"],
                mime="application/pdf"
            )

# ================= RIWAYAT =================
elif menu == "Riwayat Kalibrasi":
    st.title("📚 Riwayat Kalibrasi")

    if len(st.session_state.riwayat) > 0:
        st.dataframe(
            pd.DataFrame(st.session_state.riwayat),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Belum ada riwayat.")

# ================= EXPORT =================
elif menu == "Export Excel":
    st.title("📥 Export Data Excel")

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:
        df_status.to_excel(
            writer,
            sheet_name="Data Kalibrasi",
            index=False
        )

        pd.DataFrame(
            st.session_state.riwayat
        ).to_excel(
            writer,
            sheet_name="Riwayat",
            index=False
        )

    st.download_button(
        label="Download Excel",
        data=output.getvalue(),
        file_name="data_kalibrasi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
