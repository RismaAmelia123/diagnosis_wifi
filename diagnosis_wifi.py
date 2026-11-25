import streamlit as st

# ---------------------------------------------------------------- KNOWLEDGE BASE
ATURAN_WIFI = [
    ("W1", {"router_lampu_mati", "kabel_daya_terpasang"}, "adaptor_router_bermasalah"),
    ("W2", {"adaptor_router_bermasalah"}, "router_tak_bertenaga"),
    ("W3", {"router_tak_bertenaga", "ada_adaptor_cadangan"}, "solusi_ganti_adaptor"),
    ("W4", {"router_tak_bertenaga", "tidak_ada_adaptor_cadangan"}, "solusi_beli_adaptor"),
    ("W5", {"router_lampu_menyala", "laptop_tidak_dapat_ip"}, "masalah_dhcp_atau_sinyal"),
    ("W6", {"masalah_dhcp_atau_sinyal", "wifi_laptop_aktif"}, "router_perlu_restart"),
    ("W7", {"router_perlu_restart"}, "solusi_restart_router"),
    ("W8", {"masalah_dhcp_atau_sinyal", "wifi_laptop_nonaktif"}, "solusi_aktifkan_wifi_laptop"),
]
KONKLUSI = {k for _, _, k in ATURAN_WIFI}
SOLUSI = sorted(k for k in KONKLUSI if k.startswith("solusi_"))

GRUP = {
    "📡 Kondisi Router": [("router_lampu_mati", "🔴", "Lampu router mati"),
                          ("router_lampu_menyala", "🟢", "Lampu router menyala"),
                          ("kabel_daya_terpasang", "🔌", "Kabel daya terpasang")],
    "🔋 Adaptor": [("ada_adaptor_cadangan", "✅", "Ada adaptor cadangan"),
                   ("tidak_ada_adaptor_cadangan", "❌", "Tidak ada adaptor cadangan")],
    "💻 Laptop": [("laptop_tidak_dapat_ip", "🚫", "Laptop tidak dapat IP"),
                  ("wifi_laptop_aktif", "📶", "Wi-Fi laptop aktif"),
                  ("wifi_laptop_nonaktif", "✈️", "Wi-Fi laptop nonaktif")],
}
FAKTA_DASAR = [f for g in GRUP.values() for f, _, _ in g]

SARAN = {
    "solusi_ganti_adaptor": ("🔄", "Ganti Adaptor", "Pasang adaptor cadangan pada router, lalu cek apakah lampu menyala."),
    "solusi_beli_adaptor": ("🛒", "Beli Adaptor Baru", "Adaptor rusak dan tidak ada cadangan. Beli adaptor baru yang sesuai voltase router."),
    "solusi_restart_router": ("🔁", "Restart Router", "Cabut daya router 30 detik, colokkan lagi, tunggu hingga semua lampu stabil."),
    "solusi_aktifkan_wifi_laptop": ("📲", "Aktifkan Wi-Fi Laptop", "Nyalakan Wi-Fi di laptop (tombol Fn atau pengaturan jaringan), lalu sambungkan ulang."),
}
PRESET = {
    "🔄 Ganti adaptor": {"router_lampu_mati", "kabel_daya_terpasang", "ada_adaptor_cadangan"},
    "🛒 Beli adaptor": {"router_lampu_mati", "kabel_daya_terpasang", "tidak_ada_adaptor_cadangan"},
    "🔁 Restart router": {"router_lampu_menyala", "laptop_tidak_dapat_ip", "wifi_laptop_aktif"},
    "📲 Aktifkan Wi-Fi": {"router_lampu_menyala", "laptop_tidak_dapat_ip", "wifi_laptop_nonaktif"},
}


def h(x):
    return x.replace("_", " ")


# JALANKAN PENALARAN
def forward_chaining(fakta_awal):
    fakta, langkah, berubah = set(fakta_awal), [], True
    while berubah:
        berubah = False
        for nama, premis, konklusi in ATURAN_WIFI:
            if konklusi not in fakta and premis <= fakta:
                fakta.add(konklusi)
                langkah.append((nama, sorted(premis), konklusi))
                berubah = True
    return langkah, fakta


def backward_chaining(tujuan, fakta, log, depth=0, stack=None):
    stack = stack or set()
    if tujuan in fakta:
        log.append((depth, "ok", f"<b>{h(tujuan)}</b> ada di fakta"))
        return True
    if tujuan in stack:
        return False
    log.append((depth, "ask", f"Buktikan <b>{h(tujuan)}</b>?"))
    for nama, premis, konklusi in ATURAN_WIFI:
        if konklusi != tujuan:
            continue
        log.append((depth, "try", f"Coba aturan <b>{nama}</b>, butuh: {', '.join(h(p) for p in sorted(premis))}"))
        if all(backward_chaining(p, fakta, log, depth + 1, stack | {tujuan}) for p in sorted(premis)):
            log.append((depth, "ok", f"{nama} terpenuhi, <b>{h(tujuan)}</b> TERBUKTI"))
            return True
        log.append((depth, "fail", f"{nama} gagal"))
    log.append((depth, "fail", f"<b>{h(tujuan)}</b> TIDAK TERBUKTI"))
    return False


# UI
st.set_page_config(page_title="Diagnosis Wi-Fi", page_icon="📶", layout="wide")
st.markdown("""
<style>
.hero{background:linear-gradient(135deg,#4f46e5 0%,#06b6d4 100%);padding:2rem 2.2rem;border-radius:20px;
      color:white;margin-bottom:1.2rem;box-shadow:0 10px 30px rgba(79,70,229,.25)}
.hero h1{margin:0;font-size:2.1rem;color:white}
.hero p{margin:.4rem 0 0;opacity:.9;font-size:1.05rem}
.card{border:1px solid rgba(128,128,128,.25);border-radius:16px;padding:1rem 1.2rem;margin-bottom:.8rem;
      background:rgba(128,128,128,.06)}
.step{display:flex;gap:.9rem;align-items:flex-start;border-left:4px solid #6366f1;padding:.7rem 1rem;
      margin:.5rem 0;border-radius:0 12px 12px 0;background:rgba(99,102,241,.08)}
.badge{background:#6366f1;color:white;border-radius:8px;padding:.15rem .6rem;font-weight:700;font-size:.85rem}
.sol{background:linear-gradient(135deg,#16a34a,#22c55e);color:white;border-radius:18px;padding:1.4rem 1.6rem;
     margin-top:1rem;box-shadow:0 8px 24px rgba(34,197,94,.3)}
.sol h2{margin:0;color:white}.sol p{margin:.4rem 0 0;opacity:.95}
.nosol{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.4);border-radius:16px;padding:1.1rem 1.4rem}
.tree{font-family:ui-monospace,Consolas,monospace;font-size:.92rem;padding:.3rem .7rem;margin:.15rem 0;border-radius:8px}
.tree.ask{background:rgba(59,130,246,.12)}.tree.try{background:rgba(234,179,8,.15)}
.tree.ok{background:rgba(34,197,94,.15)}.tree.fail{background:rgba(239,68,68,.15)}
</style>
<div class="hero"><h1>📶 Sistem Pakar Diagnosis Wi-Fi</h1>
<p>Temukan penyebab koneksi bermasalah dengan <b>Forward</b> &amp; <b>Backward Chaining</b> berbasis aturan W1–W8</p></div>
""", unsafe_allow_html=True)

for f in FAKTA_DASAR:
    st.session_state.setdefault(f"f_{f}", False)


def set_preset(fakta):
    for f in FAKTA_DASAR:
        st.session_state[f"f_{f}"] = f in fakta


with st.sidebar:
    st.header("⚡ Skenario Cepat")
    st.caption("Klik untuk mengisi gejala otomatis")
    for nama, fakta in PRESET.items():
        st.button(nama, on_click=set_preset, args=(fakta,), use_container_width=True)
    st.button("🧹 Kosongkan", on_click=set_preset, args=(set(),), use_container_width=True)
    st.divider()
    st.caption("Forward: fakta ➜ solusi\n\nBackward: dugaan ➜ pembuktian")

st.subheader("1️⃣ Pilih gejala yang terjadi")
for col, (judul, items) in zip(st.columns(3), GRUP.items()):
    with col:
        with st.container(border=True):
            st.markdown(f"**{judul}**")
            for f, ikon, label in items:
                st.checkbox(f"{ikon} {label}", key=f"f_{f}")

fakta_dipilih = {f for f in FAKTA_DASAR if st.session_state[f"f_{f}"]}
if {"router_lampu_mati", "router_lampu_menyala"} <= fakta_dipilih:
    st.warning("Lampu router tidak mungkin mati dan menyala sekaligus.")
if {"ada_adaptor_cadangan", "tidak_ada_adaptor_cadangan"} <= fakta_dipilih:
    st.warning("Pilih salah satu: ada atau tidak ada adaptor cadangan.")
if {"wifi_laptop_aktif", "wifi_laptop_nonaktif"} <= fakta_dipilih:
    st.warning("Wi-Fi laptop tidak mungkin aktif dan nonaktif sekaligus.")

st.subheader("2️⃣ Jalankan penalaran")
tab_f, tab_b, tab_a = st.tabs(["➡️ Forward Chaining", "⬅️ Backward Chaining", "📚 Aturan W1–W8"])

langkah, fakta_akhir = forward_chaining(fakta_dipilih)

with tab_f:
    st.write("Dari fakta yang dipilih, program menerapkan aturan satu per satu sampai ditemukan solusi.")
    if st.button("🚀 Jalankan Forward Chaining", type="primary"):
        if not fakta_dipilih:
            st.warning("Pilih minimal satu gejala dulu.")
        else:
            solusi = sorted(f for f in fakta_akhir if f.startswith("solusi_"))
            m1, m2, m3 = st.columns(3)
            m1.metric("Fakta awal", len(fakta_dipilih))
            m2.metric("Aturan terpakai", len(langkah))
            m3.metric("Solusi ditemukan", len(solusi))
            for i, (nama, premis, konklusi) in enumerate(langkah, 1):
                st.markdown(
                    f'<div class="step"><span class="badge">{nama}</span><div><b>Langkah {i}</b><br>'
                    f'Karena <i>{" + ".join(h(p) for p in premis)}</i> ➜ <b>{h(konklusi)}</b></div></div>',
                    unsafe_allow_html=True)
            if solusi:
                for s in solusi:
                    ikon, judul, saran = SARAN[s]
                    st.markdown(f'<div class="sol"><h2>{ikon} Solusi: {judul}</h2><p>{saran}</p></div>',
                                unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown('<div class="nosol"><b>😕 Belum ada solusi.</b><br>Fakta belum memenuhi syarat '
                            'aturan mana pun. Coba tambah gejala atau pakai Skenario Cepat di sidebar.</div>',
                            unsafe_allow_html=True)

with tab_b:
    st.write("Pilih dugaan solusi, lalu program membuktikannya mundur sampai ke fakta.")
    hipotesis = st.selectbox("Dugaan solusi:", SOLUSI,
                             format_func=lambda s: f"{SARAN[s][0]} {SARAN[s][1]}")
    if st.button("🔍 Buktikan dugaan", type="primary"):
        if not fakta_dipilih:
            st.warning("Pilih minimal satu gejala dulu.")
        else:
            log = []
            ok = backward_chaining(hipotesis, fakta_dipilih, log)
            ikon_map = {"ask": "❓", "try": "📖", "ok": "✅", "fail": "❌"}
            st.markdown("".join(
                f'<div class="tree {k}" style="margin-left:{d * 28}px">{ikon_map[k]} {t}</div>'
                for d, k, t in log), unsafe_allow_html=True)
            if ok:
                _, judul, saran = SARAN[hipotesis]
                st.markdown(f'<div class="sol"><h2>✅ TERBUKTI: {judul}</h2><p>{saran}</p></div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="nosol"><b>❌ TIDAK TERBUKTI: {SARAN[hipotesis][1]}</b><br>'
                            'Ada syarat yang tidak didukung fakta (lihat baris merah di atas).</div>',
                            unsafe_allow_html=True)

with tab_a:
    for nama, premis, konklusi in ATURAN_WIFI:
        st.markdown(
            f'<div class="card"><span class="badge">{nama}</span> &nbsp; <b>JIKA</b> '
            f'{" <b>DAN</b> ".join(h(p) for p in sorted(premis))} &nbsp;<b>MAKA</b> '
            f'<span style="color:#6366f1"><b>{h(konklusi)}</b></span></div>', unsafe_allow_html=True)