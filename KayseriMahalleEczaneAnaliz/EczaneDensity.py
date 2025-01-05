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