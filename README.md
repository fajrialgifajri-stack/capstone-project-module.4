# 🏗️ SafeSite — Construction Safety Monitoring Berbasis Computer Vision
Capstone Project Module 4 — Computer Vision

---

## 📌 Deskripsi Proyek
**SafeSite** adalah aplikasi *automated safety monitoring* bertenaga Computer Vision yang dirancang untuk mendeteksi kepatuhan Alat Pelindung Diri (APD) pekerja di area konstruksi secara otomatis. 

### 💥 Latar Belakang & Masalah
* **Risiko Industri Tertinggi:** Industri konstruksi menyumbang fatalitas kerja tertinggi sebesar 20.4% (1,034 fatalitas per tahun), didominasi oleh cedera parah pada area vital kepala dan torso (67,500+ kasus).
* **Keterbatasan Pengawasan Manual:** Rasio pengawas lapangan tidak sebanding dengan luasnya area proyek dan ratusan pekerja, memicu tingginya risiko kelalaian manusia (*human error*).
* **Solusi:** Mengotomatisasi pemantauan kepatuhan APD (`helmet` & `vest`) secara *real-time* untuk mempermudah tugas *Site Manager* atau *Auditor K3*.

### 🎯 Objektif Utama
1. **Object Detection:** Membangun model deep learning yang mampu mengenali 5 kelas: `person`, `helmet`, `no-helmet`, `vest`, dan `no-vest`.
2. **Per-Worker APD Assignment:** Mengimplementasikan **IoU-based matching** untuk menganalisis kepatuhan APD secara individual per pekerja.
3. **Safety Analytics:** Menghitung *Severity Score (0–100)* dengan *weighted penalty* untuk menghasilkan penilaian *Safety Grade (A–F)* area kerja.
4. **Web Deployment:** Menyediakan interface interaktif berbasis Streamlit Cloud yang dapat diakses publik.

---

## 🏗️ Alur Kerja Sistem (Pipeline)

```text
  [ Input Image ] ──> [ Preprocessing & Resize (640x640) ]
                             │
                             ▼
              [ Inference Engine: YOLOv8n ]
                             │
                             ▼
                 [ Bounding Box Outputs ]
            (person, helmet, no-helmet, vest, no-vest)
                             │
                             ▼
              [ IoU-Based Matching Engine ] 
        (Memasangkan APD ke objek person terdekat)
                             │
                             ▼
             [ Scoring & Analytics Process ]
        (Kalkulasi Severity Score & Safety Grade A-F)
                             │
                             ▼
   [ Streamlit UI Visualisation (Bounding Box + Dashboard) ]
---

## 🛠️ Tech Stack

| Komponen | Teknologi |
|---|---|
| Core Architecture | PyTorch / Ultralytics (YOLO) |
| Model Weights | best_construction.pt |
| Image Processing | OpenCV / Pillow |
| Frontend UI | Streamlit |

---

## ⚙️ Instalasi

### 1. Clone repository
```bash
git clone https://github.com/username/capstone-project-module.4.git
cd capstone-project-module.4
```

### 2. Buat virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi
```bash
streamlit run app.py
```

---

---

## 📁 Struktur Project

```
capstone-project-module.4/
│
├── app.py                  # Core script untuk frontend Streamlit & logika inference
├── best_construction.pt    # Pre-trained weights hasil training model Deep Learning
└── requirements.txt        # Daftar library dependency project
```

---

## Hasil Model & Evaluasi

Metrik Evaluasi: nilai mAP@50 mencapai 83,86%, tingkat Recall di 81,26%, dan Precision di 79,03%.

---

## ⚠️ Known Limitations

- no-helmet hanya 64.75% mAP akibat class imbalance ekstrem (1.7% dari total data)
- IoU assignment bisa gagal pada kerumunan padat karena bbox saling overlap
- Model dilatih pada gambar statis — belum diuji untuk video stream real-time

---

## 🚀 Future Improvements

- Tambah data no-helmet atau terapkan weighted loss untuk atasi class imbalance
- Integrasi CCTV video stream untuk monitoring area konstruksi secara live
- Tambah fitur alert system — notifikasi otomatis ke supervisor saat violation terdeteksi

---

## 👤 Author

Fajri Algifari
