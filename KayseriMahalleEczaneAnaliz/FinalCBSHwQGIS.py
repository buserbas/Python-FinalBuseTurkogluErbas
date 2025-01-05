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
 