# Sistem File Management
Aplikasi simulasi sistem file dengan implementasi alokasi berurutan (Contiguous Allocation) untuk mempelajari konsep manajemen penyimpanan pada sistem operasi.

## Anggota Kelompok
- Hasbi Haqqul Fikri (2309245)
- Putra Hadiyanto Nugroho (2308163)
- Yazid Madarizel (2305328)
- Yusrilia Hidayanti (2306828)

## Deskripsi

Sistem File Management adalah aplikasi berbasis GUI yang menyimulasikan manajemen file pada sistem operasi dengan menggunakan metode alokasi berurutan (contiguous allocation). Aplikasi ini memungkinkan pengguna untuk melakukan operasi dasar file system seperti membuat, menghapus, melihat, dan mengedit file serta direktori.

## Fitur

- **File Explorer**: Tampilan grafis untuk menjelajahi struktur direktori dan file
- **Terminal**: Antarmuka command-line untuk interaksi dengan sistem file
- **Visualisasi Alokasi**: Representasi visual blok-blok penyimpanan dan alokasi file
- **Manajemen File dan Direktori**:
  - Membuat file dan direktori baru
  - Menghapus file dan direktori
  - Mengganti nama file dan direktori
  - Melihat isi file
  - Melihat properti file dan direktori
- **Contiguous Allocation**: Implementasi algoritma alokasi berurutan untuk file

## Struktur Proyek

- `main.py` - Entry point aplikasi
- `filesystem.py` - Implementasi operasi sistem file dan struktur data
- `gui.py` - Implementasi antarmuka grafis menggunakan Tkinter
- `storage_manager.py` - Pengelolaan alokasi penyimpanan dengan metode contiguous
- `filesystem.json` - Penyimpanan data sistem file
- `storage.json` - Penyimpanan data alokasi blok

## Konsep Contiguous Allocation

Sistem ini mengimplementasikan metode alokasi berurutan (contiguous allocation) dimana:

- Disk dibagi menjadi blok-blok dengan ukuran tetap
- Setiap file menempati blok-blok berurutan pada disk
- Metadata file menyimpan nomor blok awal dan jumlah blok yang dialokasikan
- Algoritma first-fit digunakan untuk menemukan ruang kosong yang cukup

Kelebihan:
- Akses sekuensial dan random sangat cepat
- Implementasi sederhana

Kekurangan:
- Fragmentasi eksternal
- Sulit memperbesar ukuran file yang sudah ada

## Cara Menjalankan

1. Pastikan Python 3 telah terinstal
2. Clone repositori ini
3. Jalankan aplikasi:
   ```
   python main.py
   ```

## Perintah Terminal

Terminal mendukung perintah berikut:
- `ls [path]` - Menampilkan isi direktori
- `cd [path]` - Berpindah direktori
- `cd ..` - Berpindah ke direktori induk
- `mkdir <dir>` - Membuat direktori baru
- `touch <file>` - Membuat file baru
- `rm <path>` - Menghapus file atau direktori
- `cat <file>` - Menampilkan isi file
- `df` - Menampilkan informasi penggunaan disk
- `clear` - Membersihkan layar terminal
- `help` - Menampilkan daftar perintah

## Kebutuhan Sistem

- Python 3.6 atau lebih baru
- Tkinter (biasanya sudah termasuk dalam instalasi Python standar)

## Pengembangan

Proyek ini dikembangkan untuk tujuan pendidikan dalam memahami konsep manajemen penyimpanan pada sistem operasi.
