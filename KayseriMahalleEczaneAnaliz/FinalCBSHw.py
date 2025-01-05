# This is the final project to show Kayseri mahalle sınırları and kayseri pharmacy points and analyse

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch


# Veriye göre mahallelere verileri eklemek için fonksiyon
def add_data_to_areas(areas_gdf, data_gdf, data_column_name, distance_threshold=1000):
    """
    Verilen veri setindeki noktaların mahallelere yakınlıklarına göre sayısını mahalleler veri setine ekler.

    Parameters:
    - areas_gdf: Mahalleler veri seti (GeoDataFrame).
    - data_gdf: Eczaneler veya Aile Sağlık Merkezleri veri seti (GeoDataFrame).
    - data_column_name: Eczaneler veya Aile Sağlık Merkezlerinin adını içeren sütun ismi (string).
    - distance_threshold: Hesaplama sırasında mesafe eşik değeri (metre cinsinden). Varsayılan 1000 metre.

    Returns:
    - Güncellenmiş areas_gdf, yeni verileri içeren.
    """
    # Her mahalle için yakınındaki verileri sayma
    counts = []
    for area in areas_gdf.geometry:
        # Her mahalleye olan mesafeyi hesapla
        distance = data_gdf.distance(area)
        # Belirli bir mesafe içinde olanları say
        nearby_data = data_gdf[distance <= distance_threshold]
        counts.append(len(nearby_data))

    # Yeni sütunu ekleyin
    areas_gdf[data_column_name] = counts
    return areas_gdf


# Shapefile'larını yükleme
mahalleler = gpd.read_file("data/kayseri_mahalleler.shp")
eczaneler = gpd.read_file("data/kayseri_eczaneler.shp")
aile_saglik_merkezleri = gpd.read_file("data/Kayseri_Aile_Saglik_Merkezleri.shp")

# Mahalleler CRS'sini belirleme (Varsayımsal olarak EPSG:4326)
mahalleler.set_crs('EPSG:4326', allow_override=True, inplace=True)

# CRS'leri kontrol etme ve uyumlu hale getirme
print("Mahalleler CRS:", mahalleler.crs)
print("Eczaneler CRS:", eczaneler.crs)
print("Aile Sağlık Merkezleri CRS:", aile_saglik_merkezleri.crs)

# Projeksiyonlu CRS'ye dönüştürme (EPSG:3857)
mahalleler = mahalleler.to_crs(epsg=3857)
eczaneler = eczaneler.to_crs(epsg=3857)
aile_saglik_merkezleri = aile_saglik_merkezleri.to_crs(epsg=3857)

# Eczane sayısını mahalleler veri setine ekleme
mahalleler = add_data_to_areas(mahalleler, eczaneler, 'eczane_sayisi')

# Aile Sağlık Merkezi sayısını mahalleler veri setine ekleme
mahalleler = add_data_to_areas(mahalleler, aile_saglik_merkezleri, 'aile_saglik_sayisi')

# Mahalleler ve Eczaneleri görselleştirme (figsize daha büyük yapıldı)
fig, ax = plt.subplots(figsize=(15, 15), dpi=100)  # dpi ve figsize ile daha büyük harita

# Mahallelerin sınırlarını çizme
mahalleler.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.5)

# Eczanelerin konumlarını çizme
eczaneler.plot(ax=ax, color='red', markersize=5, label='Eczane')  # markersize büyütüldü

# Aile Sağlık Merkezlerinin konumlarını çizme
aile_saglik_merkezleri.plot(ax=ax, color='green', markersize=20, label='Aile Sağlık Merkezi')

# Başlık ve etiketler
ax.set_title('Kayseri Mahalleler, Eczaneler ve Aile Sağlık Merkezleri', fontsize=20)
ax.set_xlabel('Koordinatlar', fontsize=14)
ax.set_ylabel('Koordinatlar', fontsize=14)

# Eczane sayısını mahallelerde sol üst köşeye yazma
for _, row in mahalleler.iterrows():
    x, y = row['geometry'].bounds[0], row['geometry'].bounds[3]  # Sol üst köşe koordinatları
    label = row["eczane_sayisi"]
    if not pd.isna(label):  # NaN değerini kontrol et
        ax.text(x, y, str(int(label)), fontsize=5, ha='left', color='black', weight='bold')

# Aile Sağlık Merkezi sayısını mahallelerde sol üst köşeye yazma
for _, row in mahalleler.iterrows():
    x, y = row['geometry'].bounds[2], row['geometry'].bounds[3]  # sağ üst köşe koordinatları
    label = row["aile_saglik_sayisi"]
    if not pd.isna(label):  # NaN değerini kontrol et
        ax.text(x, y, str(int(label)), fontsize=5, ha='right', color='green', weight='bold')

# Haritayı gösterme
ax.legend()
#plt.show()

###################################################################################################
# Analysis
###################################################################################################
# Eczane Yoğunluk analizi
# Eczane Yoğunluğu Hesaplama: Eczane Sayısı / Mahalle Alanı
mahalleler['eczane_yogunlugu'] = mahalleler['eczane_sayisi'] / mahalleler['ALAN']

# Yoğunluğu harita üzerinde görselleştirme
fig, ax = plt.subplots(figsize=(15, 15), dpi=200)
mahalleler.plot(ax=ax, column='eczane_yogunlugu', cmap='Reds', legend=True, legend_kwds={'label': "Eczane Yoğunluğu (eczane/alan)"})
ax.set_title('Eczane Yoğunluğu - Kayseri Mahalleleri', fontsize=20)
ax.set_xlabel('Koordinatlar', fontsize=14)
ax.set_ylabel('Koordinatlar', fontsize=14)

# Mahallelerin sınırlarını (contour) çizdirin
mahalleler.boundary.plot(
    ax=ax,
    color='black',  # Sınırların rengi
    linewidth=0.5,  # Çizgi kalınlığı
    label='Mahalle Sınırları'  # Legend için açıklama
)

plt.show()
# Aile sağlığı yoğunluk haritası
# Aile Sağlık Merkezi Yoğunluğu Hesaplama: Aile Sağlık Merkezi Sayısı / Mahalle Alanı
mahalleler['aile_saglik_yogunlugu'] = mahalleler['aile_saglik_sayisi'] / mahalleler['ALAN']

# Yoğunluğu harita üzerinde görselleştirme
fig, ax = plt.subplots(figsize=(15, 15), dpi=200)
mahalleler.plot(ax=ax, column='aile_saglik_yogunlugu', cmap='Reds', legend=True, legend_kwds={'label': "Aile Sağlık Merkezi Yoğunluğu (merkez/alan)"})
ax.set_title('Aile Sağlık Merkezi Yoğunluğu - Kayseri Mahalleleri', fontsize=20)
ax.set_xlabel('Koordinatlar', fontsize=14)
ax.set_ylabel('Koordinatlar', fontsize=14)
# Mahallelerin sınırlarını (contour) çizdirin
mahalleler.boundary.plot(
    ax=ax,
    color='black',  # Sınırların rengi
    linewidth=0.5,  # Çizgi kalınlığı
    label='Mahalle Sınırları'  # Legend için açıklama
)

plt.show()

# Eczane vs Sağlık Ocaği karşılaştırması
# Eczane ve Aile Sağlık Merkezi Yoğunluklarını Karşılaştırma
fig, ax = plt.subplots(figsize=(15, 15), dpi=200)

# Eczane yoğunluğunu görselleştir
mahalleler.plot(ax=ax, column='eczane_yogunlugu', cmap='Reds', legend=True, alpha=1, legend_kwds={'label': "Eczane Yoğunluğu (eczane/alan)"})

# Aile Sağlık Merkezi yoğunluğunu görselleştir
mahalleler.plot(ax=ax, column='aile_saglik_yogunlugu', cmap='Blues', alpha=1, legend=True, legend_kwds={'label': "Aile Sağlık Merkezi Yoğunluğu (merkez/alan)"})

# Mahallelerin sınırlarını (contour) çizdirin
mahalleler.boundary.plot(
    ax=ax,
    color='black',  # Sınırların rengi
    linewidth=0.1,  # Çizgi kalınlığı
    label='Mahalle Sınırları'  # Legend için açıklama
)

ax.set_title('Eczane ve Aile Sağlık Merkezi Yoğunlukları - Kayseri Mahalleleri', fontsize=20)
ax.set_xlabel('Koordinatlar', fontsize=14)
ax.set_ylabel('Koordinatlar', fontsize=14)
plt.show()

# Zonlama Analizi - Eczane ve sağlık ocağı bulunmayan yerler
# 1000 metre mesafede eczane bulunmayan mahalleleri tespit et
threshold_distance = 1000  # Mesafe eşiği 1 km
eczane_yok = []

for area in mahalleler.geometry:
    # Her mahalle için en yakın eczane mesafesini hesapla
    min_distance = eczaneler.distance(area).min()
    if min_distance > threshold_distance:
        eczane_yok.append(True)
    else:
        eczane_yok.append(False)

mahalleler['eczane_yok'] = eczane_yok

# Eczane olmayan mahalleleri görselleştirme
fig, ax = plt.subplots(figsize=(15, 15), dpi=200)
mahalleler[mahalleler['eczane_yok']].plot(ax=ax, color='lightblue', edgecolor='black', alpha=1)
mahalleler[~mahalleler['eczane_yok']].plot(ax=ax, color='red', edgecolor='black', alpha=0.5)

# Mahallelerin sınırlarını (contour) çizdirin
mahalleler.boundary.plot(
    ax=ax,
    color='black',  # Sınırların rengi
    linewidth=0.1,  # Çizgi kalınlığı
    label='Mahalle Sınırları'  # Legend için açıklama
)

ax.set_title('Eczane Olmayan Mahalleler - Kayseri', fontsize=20)
ax.set_xlabel('Koordinatlar', fontsize=14)
ax.set_ylabel('Koordinatlar', fontsize=14)

# Özel Legend Ekleyin
legend_elements = [
    Patch(facecolor='lightblue', edgecolor='black', label='Eczane Yok'),
    Patch(facecolor='red', edgecolor='black', label='Eczane Var')
]

ax.legend(handles=legend_elements, loc='upper right', title='Kategori')


plt.show()

# İstatistik analizi
# Eczane sayılarının istatistiksel özeti
eczane_istatistikleri = mahalleler['eczane_sayisi'].describe()
print("Eczane Sayıları İstatistikleri:\n", eczane_istatistikleri)

# Aile Sağlık Merkezi sayılarının istatistiksel özeti
aile_saglik_istatistikleri = mahalleler['aile_saglik_sayisi'].describe()
print("Aile Sağlık Merkezi Sayıları İstatistikleri:\n", aile_saglik_istatistikleri)












