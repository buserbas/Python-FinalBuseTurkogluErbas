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
