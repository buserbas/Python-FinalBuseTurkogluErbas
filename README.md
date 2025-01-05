# Python-FinalBuseTurkogluErbas
Bı dosya içerisinde final ödevinin açıklaması ve final ödevi iin geliştirilmiş python kodları (pycharmda ve visual studio ortamında geliştirmemi yaptım) ile birlikte bu python kodlarının qgis uygulamasına port edilerek layerlar eklenip layerlar üzerinde yapılan analizlerin kodlarını bulabilirsiniz.

ÖNEMLİ NOT : kodları yazarken shape dosyalarının pathlerinin verirken localimdeki full pathler kullandım, okuyucu kodları okuyup çalıştırması için repository/data/ içerisinde bulunan dosyaların addresslerini kendi local'ine göre full path olucak şekilde vermesi gerekmektedir. Diğer türlü çalışmayacaktır.
QGIS'e geçmeden önce pycharmda geliştirdiğim kodda önce shape dosyalarını okuyup sonrasında bu dosyalar ile aynı coğrafi coordinat sistemine bağlayıp (CRS : EPSG:4326) sonrasında
-  Kayseri eczane yoğunluk haritası
-  Kayseri eczane ve Aile sağlık merkezleri haritasını
-  Aile Sağlık Merkezi yoğunluk haritasını
-  Eczane Olmayan Mahallelerin haritasını
üretmektedir.

Bu repository içerisinde python kodlarını port ettiğim qgis projesi de mevcuttur. QGIS projesinde her bir python kodunun farklı bir görevi vardır. 
FinalCBSHwQGIS.py kodu shape dosyalarını QGIS'e bir layer olarak eklemek ve gelecek olan analizler için dataların hazırlanması görevini görmektedir.
EczaneDensity.py python kodu, QGIS'de bulunan Heatmap engine'i ile çalıştırılarak noktasal Eczane lokasyon verilerini bir heatmnap'e dönüştürerek yeni bir layer olarak eklemektedir.
ASMDensity.py python kodu, yine aynı Heatmap engine'i ile Aile Sağlık Merkezi(ASM) noktasal lokasyon verilerini bir heatmap'e dönüştürerek yeni bir layer olarak eklemektedir.
WoutASMorEczane.py kodu, mahalle layer'ı üzerinde, eczane ve ASM layerlarındaki bilgileri kullanarak mahalle layerında hem eczanelerin hem de ASMlerin bulunmadığı mahalleleri yeni bir layer olarak eklemektedir.
MahalleAdları.py kodu, mahalle layer'ı içerisindeki "ADI" fieldlarını kullanarak bunu noktasal bir layer olarak eklemektedir.

Bu yöntem ile Kayseri ilinde Eczane olmayan mahallelere ve ASM olmayan mahallelere yoğunlaşılarak bu mahallelerin sakinlerinin hayatlarını kolaylaştırmak için eczane ve
ASM gibi sağlık hizmeti sunan birimler yerleştirilebilir ve topluma yarar sağlanabilir.

------------------------------------------------------------------------
- Pycharm/Visual Studio Python Kodları - (Bu kodları repository içerisinde FinalCBSHW.py içerisinde bulabilirsiniz)
------------------------------------------------------------------------
# This is the final project to show Kayseri mahalle sınırları and kayseri pharmacy points and analyse

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch
# Veriye göre mahallelere verileri eklemek için fonksiyon
def add_data_to_areas(areas_gdf, data_gdf, data_column_name, distance_threshold=1000):

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

------------------------------------------------------------------------
- QGIS'e port edilmiş plugin python kodları - (Bu kodları repository içerisinde FinalCBSHWQGIS.py, ASMDensity.py, EczaneDensity.py,
- MahalleAdları.py, WoutASMorEczane.py  içerisinde bulabilirsiniz)
------------------------------------------------------------------------
- FinalCBSHwQGIS.py -
- ------------------------------------------------------------------------
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsField,
    QgsFeature
)
from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsProject, QgsPalLayerSettings, QgsTextFormat, QgsVectorLayer
from qgis.gui import QgsMapCanvas

# 1. Katmanları Yükleme
mahalleler_path = "C:/Users/ibgre/Desktop/BuseKod/KayseriMahalleEczaneAnaliz/data/kayseri_mahalleler.shp"  # Mahalleler shapefile yolu
eczaneler_path = "C:/Users/ibgre/Desktop/BuseKod/KayseriMahalleEczaneAnaliz/data/kayseri_eczaneler.shp"  # Eczaneler shapefile yolu
asm_path = "C:/Users/ibgre/Desktop/BuseKod/KayseriMahalleEczaneAnaliz/data/Kayseri_Aile_Saglik_Merkezleri.shp"  # ASM shapefile yolu

mahalleler_layer = QgsVectorLayer(mahalleler_path, "Kayseri Mahalleler", "ogr")
eczaneler_layer = QgsVectorLayer(eczaneler_path, "Kayseri Eczaneler", "ogr")
asm_layer = QgsVectorLayer(asm_path, "Kayseri ASM", "ogr")

# Katmanları Projeye Ekleme
if mahalleler_layer.isValid():
    QgsProject.instance().addMapLayer(mahalleler_layer)
    print("Mahalleler katmanı yüklendi.")
else:
    print("Mahalleler katmanı yüklenemedi.")

if eczaneler_layer.isValid():
    QgsProject.instance().addMapLayer(eczaneler_layer)
    print("Eczaneler katmanı yüklendi.")
else:
    print("Eczaneler katmanı yüklenemedi.")

if asm_layer.isValid():
    QgsProject.instance().addMapLayer(asm_layer)
    print("ASM katmanı yüklendi.")
else:
    print("ASM katmanı yüklenemedi.")

# 2. Yeni Alanlar Ekleyerek Eczane ve ASM Sayılarını Hesaplama
mahalleler_layer.startEditing()

# Alanlar zaten varsa, eklemeye gerek yok.
fields = mahalleler_layer.fields()
if "eczane_say" not in fields.names():
    print("eczane_say alan adı mevcut değil, ekleniyor")
    eczane_field = QgsField("eczane_say", QVariant.Int)  # Kısa isim kullanıyoruz
    mahalleler_layer.dataProvider().addAttributes([eczane_field])

if "asm_sayisi" not in fields.names():
    print("asm_sayisi alan adı mevcut değil, ekleniyor")
    asm_field = QgsField("asm_sayisi", QVariant.Int)  # Kısa isim kullanıyoruz
    mahalleler_layer.dataProvider().addAttributes([asm_field])

mahalleler_layer.updateFields()

print(mahalleler_layer.fields().names())  # Alan isimlerini yazdırma
# Her mahalle için eczane ve ASM sayısı hesaplama
for mahalle in mahalleler_layer.getFeatures():
    eczane_count = 0
    asm_count = 0
    mahalle_geom = mahalle.geometry()

    # Eczaneler için mekansal içerme kontrolü
    for eczane in eczaneler_layer.getFeatures():
        if mahalle_geom.contains(eczane.geometry()):
            eczane_count += 1

    # ASM için mekansal içerme kontrolü
    for asm in asm_layer.getFeatures():
        if mahalle_geom.contains(asm.geometry()):
            asm_count += 1

    # Sonuçları güncelleme
    mahalle["eczane_say"] = eczane_count  # Güncellenen alan adı
    mahalle["asm_sayisi"] = asm_count  # Güncellenen alan adı
    mahalleler_layer.updateFeature(mahalle)

mahalleler_layer.commitChanges()

# 3. Görselleştirme: Mahallelerin Kontur Çizgilerini ve Sayıları Gösterme
# Sayıları haritaya yazdırma
for mahalle in mahalleler_layer.getFeatures():
    geom = mahalle.geometry()
    centroid = geom.centroid()
    x, y = centroid.asPoint().x(), centroid.asPoint().y()
    ecz_sayi = mahalle["eczane_say"]
    asm_sayi = mahalle["asm_sayisi"]

   # # NaN kontrolü ve yazı ekleme
   # if ecz_sayi is not None:
   #     iface.mapCanvas().scene().addTextLabel(
   #         str(ecz_sayi),
   #         x, y,
   #         color="blue",
   #         size=12
   #     )
   # if asm_sayi is not None:
   #     iface.mapCanvas().scene().addTextLabel(
   #         str(asm_sayi),
   #         x, y + 50,  # Sayılar çakışmasın diye biraz yukarı kaydırdık
   #         color="red",
   #         size=12
   #     )
# Katmanı yükle
mahalleler_layer = QgsProject.instance().mapLayersByName("Kayseri Mahalleler")[0]

# Etiketleme ayarlarını başlat
label_settings = QgsPalLayerSettings()
label_settings.fieldName = 'ecz_sayi'  # Etiketlemek istediğiniz alanın adı

# Metin formatını ayarlayın
text_format = QgsTextFormat()
text_format.setSize(10)  # Yazı tipi boyutu
text_format.setColor(Qt.black)  # Yazı rengi

label_settings.setFormat(text_format)  # Yazı formatını ayarlayın

# Etiketleme ayarlarını katmana uygulama
mahalleler_layer.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))

# Etiketleri etkinleştirme
mahalleler_layer.setLabelsEnabled(True)

# Katman görünürlüğünü değiştirme
layer_tree_node = QgsProject.instance().layerTreeRoot().findLayer(mahalleler_layer.id())

# Katmanı görünür yapma
layer_tree_node.setItemVisibilityChecked(True)  # Görünür yapmak için bu fonksiyonu kullanın

# Katmanı yenileme
QgsProject.instance().layerTreeRoot().findLayer(mahalleler_layer.id()).setItemVisibilityChecked(True)
 
------------------------------------------------------------------------
- ASMDensity.py -
- ------------------------------------------------------------------------

import processing
from qgis.core import QgsProject, QgsRasterLayer, QgsProcessing

# Katmanları yükle
eczaneler_layer = QgsProject.instance().mapLayersByName('Kayseri ASM')[0]  # Eczaneler katmanını yükleyin
output_raster = "C:/Users/ibgre/Desktop/BuseKod/KayseriMahalleEczaneAnaliz/output/asm_yogunluk.tif"  # Sonuç raster dosyasının yolu
# List the parameters of the Heatmap Kernel Density Estimation algorithm
alg = processing.algorithmHelp('qgis:heatmapkerneldensityestimation')
print(alg)
# Heatmap Kernel Density Estimation aracını çalıştırma
params = {
    'INPUT': eczaneler_layer,              # Eczane katmanını input olarak veriyoruz
    'RADIUS': 0.02,                         # Kernel yarıçapını belirliyoruz (örneğin 500 m)
    'OUTPUT': output_raster,               # Sonuçların kaydedileceği dosya yolu
    'PIXEL_SIZE': 0.001,                       # Hücre boyutunu belirliyoruz (örneğin 10 m)
    'KERNEL':3,
    'OUTPUT_VALUE':0,
    'WEIGHT_FIELD': '',                    # Ağırlıklı alan varsa buraya yazın (eğer yoksa boş bırakabilirsiniz)
}

# Aracı çalıştır
result = processing.run("qgis:heatmapkerneldensityestimation", params)

# Sonuç raster dosyasını QGIS'e ekle
raster_layer = QgsRasterLayer(output_raster, 'ASM Yoğunluk Haritası')

# Raster layer başarılı bir şekilde yüklendiyse QGIS'e ekle
if raster_layer.isValid():
    QgsProject.instance().addMapLayer(raster_layer)
    print("Eczane yoğunluk haritası başarıyla QGIS'e eklendi.")
else:
    print("Raster layer geçerli değil.")
    
------------------------------------------------------------------------
- EczaneDensity.py -
- ------------------------------------------------------------------------
import processing
from qgis.core import QgsProject, QgsRasterLayer, QgsProcessing

# Katmanları yükle
eczaneler_layer = QgsProject.instance().mapLayersByName('Kayseri Eczaneler')[0]  # Eczaneler katmanını yükleyin
output_raster = "C:/Users/ibgre/Desktop/BuseKod/KayseriMahalleEczaneAnaliz/output/eczane_yogunluk.tif"  # Sonuç raster dosyasının yolu
# List the parameters of the Heatmap Kernel Density Estimation algorithm
alg = processing.algorithmHelp('qgis:heatmapkerneldensityestimation')
print(alg)
# Heatmap Kernel Density Estimation aracını çalıştırma
params = {
    'INPUT': eczaneler_layer,              # Eczane katmanını input olarak veriyoruz
    'RADIUS': 0.02,                         # Kernel yarıçapını belirliyoruz (örneğin 500 m)
    'OUTPUT': output_raster,               # Sonuçların kaydedileceği dosya yolu
    'PIXEL_SIZE': 0.001,                       # Hücre boyutunu belirliyoruz (örneğin 10 m)
    'KERNEL':1,
    'OUTPUT_VALUE':0,
    'WEIGHT_FIELD': '',                    # Ağırlıklı alan varsa buraya yazın (eğer yoksa boş bırakabilirsiniz)
}

# Aracı çalıştır
result = processing.run("qgis:heatmapkerneldensityestimation", params)

# Sonuç raster dosyasını QGIS'e ekle
raster_layer = QgsRasterLayer(output_raster, 'Eczane Yoğunluk Haritası')

# Raster layer başarılı bir şekilde yüklendiyse QGIS'e ekle
if raster_layer.isValid():
    QgsProject.instance().addMapLayer(raster_layer)
    print("Eczane yoğunluk haritası başarıyla QGIS'e eklendi.")
else:
    print("Raster layer geçerli değil.")

------------------------------------------------------------------------
- WoutASMorEczane.py -
- ------------------------------------------------------------------------
from qgis.core import QgsProject, QgsSpatialIndex, QgsVectorLayer
from PyQt5.QtCore import QVariant

# Katmanları QGIS projede bul
mahalleler_layer = QgsProject.instance().mapLayersByName('Kayseri Mahalleler')[0]
eczaneler_layer = QgsProject.instance().mapLayersByName('Kayseri Eczaneler')[0]
asm_layer = QgsProject.instance().mapLayersByName('Kayseri ASM')[0]

# Geometri için spatial index oluşturun (daha hızlı işlem için)
eczane_index = QgsSpatialIndex(eczaneler_layer.getFeatures())
asm_index = QgsSpatialIndex(asm_layer.getFeatures())

# Eczane ve ASM bulunmayan mahalleleri tespit et
eczane_olmayan_mahalleler = []
asm_olmayan_mahalleler = []

for mahalle in mahalleler_layer.getFeatures():
    # Eğer mahalle eczanelerle kesişmiyorsa, mahalleyi eczane olmayanlar listesine ekleyin
    eczane_found = False
    for eczane in eczaneler_layer.getFeatures():
        if mahalle.geometry().intersects(eczane.geometry()):
            eczane_found = True
            break
    if not eczane_found:
        eczane_olmayan_mahalleler.append(mahalle)

    # Eğer mahalle Aile Sağlık Merkezi (ASM) ile kesişmiyorsa, mahalleyi ASM olmayanlar listesine ekleyin
    asm_found = False
    for asm in asm_layer.getFeatures():
        if mahalle.geometry().intersects(asm.geometry()):
            asm_found = True
            break
    if not asm_found:
        asm_olmayan_mahalleler.append(mahalle)

# Yeni katman oluştur
fields = mahalleler_layer.fields()  # mevcut alanları al
output_layer = QgsVectorLayer('Polygon?crs=' + mahalleler_layer.crs().toWkt(), 'Eczane ve ASM Olmayan Mahalleler', 'memory')
output_layer_data = output_layer.dataProvider()

# Alanları kopyalayın
output_layer_data.addAttributes(fields)
output_layer.updateFields()

# Eczane ve ASM bulunmayan mahalleleri katmana ekleyin
output_layer.startEditing()
for mahalle in eczane_olmayan_mahalleler + asm_olmayan_mahalleler:
    output_layer_data.addFeature(mahalle)
output_layer.commitChanges()

# Katmanı projeye ekleyin
QgsProject.instance().addMapLayer(output_layer)

------------------------------------------------------------------------
- MahalleAdları.py -
- ------------------------------------------------------------------------
from qgis.core import QgsProject, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsPalLayerSettings, QgsTextFormat
from PyQt5.QtCore import QVariant

# Kayseri Mahalleler katmanını yükle
mahalleler_layer = QgsProject.instance().mapLayersByName('Kayseri Mahalleler')[0]  # Katman adı doğru olmalı

# Yeni bir vektör katmanı oluştur (Mahalle adlarını içerecek)
pr = QgsProject.instance()
new_layer = QgsVectorLayer('Point?crs=EPSG:4326', 'Mahalle Adları', 'memory')  # Memory katmanı oluşturuluyor
prov = new_layer.dataProvider()

# Yeni katmana alanlar ekle (Mahalle adı ve Nüfus)
prov.addAttributes([QgsField('Mahalle_Adi', QVariant.String),
                    QgsField('Nufus_Orani', QVariant.Double)])  # Mahalle adı ve nüfus oranı
new_layer.updateFields()

# Mahallelerin verilerini yeni katmana ekleyelim
toplam_nufus = 0  # Başlangıçta toplam nüfus sıfır olarak belirlenir
nufus_alan_adi = 'NUFUS'  # Nüfus alanı adı

# Toplam nüfusu hesapla
for feature in mahalleler_layer.getFeatures():
    nufus = feature[nufus_alan_adi]
    if isinstance(nufus, (int, float)):  # Geçerli sayısal değerleri kontrol et
        toplam_nufus += nufus

# Mahalleleri yeni katmana ekle
for feature in mahalleler_layer.getFeatures():
    mahalle_ismi = feature['ADI']  # Mahalle adı
    nufus = feature[nufus_alan_adi]
    if isinstance(nufus, (int, float)) and toplam_nufus > 0:  # Nüfus oranı hesapla
        nufus_orani = nufus / toplam_nufus
        
        # Mahalle koordinatlarını al (örneğin, geometrinin merkezini al)
        geometry = feature.geometry()
        centroid = geometry.centroid()  # Mahalle geometrisinin merkezi
        
        # Yeni feature (özellik) oluştur
        new_feature = QgsFeature()
        new_feature.setGeometry(QgsGeometry.fromPointXY(centroid.asPoint()))  # Merkez noktasını kullanıyoruz
        new_feature.setAttributes([mahalle_ismi, nufus_orani])  # Mahalle adı ve nüfus oranını ayarla
        
        # Katmana ekle
        prov.addFeature(new_feature)

# Katmanı haritaya ekle
QgsProject.instance().addMapLayer(new_layer)

# Etiketleme ayarlarını yapalım
label_settings = QgsPalLayerSettings()  # Etiketleme ayarlarını başlat
label_settings.enabled = True  # Etiketlemeyi etkinleştir
label_settings.fieldName = 'Mahalle_Adi'  # Etiket olarak 'Mahalle_Adi' kullanıyoruz

# Etiketlerin formatını ayarlayalım (isteğe bağlı)
text_format = QgsTextFormat()  # Doğru sınıf adı burada kullanıldı
text_format.setSize(10)  # Etiket boyutunu ayarlayalım
label_settings.setFormat(text_format)  # Formatı etiket ayarlarına uygula

# Katman üzerinde etiketlemeyi etkinleştirme
new_layer.setLabeling(QgsPalLayerSettings())  # SetLabeling burada doğru şekilde kullanıldı
new_layer.setLabeling(label_settings)  # Etiketleme ayarlarını katmana uygula
new_layer.triggerRepaint()  # Yeniden çizim

print("Mahalle Adları Katmanı başarıyla oluşturuldu ve haritaya eklendi.")






