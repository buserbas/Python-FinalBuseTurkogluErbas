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
