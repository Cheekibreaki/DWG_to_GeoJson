from osgeo import ogr

dxf_file = r"E:\react-naitve project\campus\src\assets\Bahen Indoor building layout\DXF\Drawing1test.dxf"
driver = ogr.GetDriverByName("DXF")
dataSource = driver.Open(dxf_file, 1)
layer = dataSource.GetLayer()
for layer in dataSource:
    layer_name = layer.GetName()
    print(layer_name)
for feature in layer:
    geometry = feature.GetGeometryRef()
    print(geometry)
# geojson_file = r"E:\react-naitve project\campus\src\assets\Bahen Indoor building layout\DXF\Drawing1test.geojson"
geojson_driver = ogr.GetDriverByName("GeoJSON")
Geojson_dataSource = geojson_driver.CreateDataSource("output1.json")
Geojson_layer = Geojson_dataSource.CreateLayer("first floor", geom_type=ogr.wkbUnknown)

for feature in layer:
        geometry = feature.GetGeometryRef()
        geojson_feature = ogr.Feature(Geojson_layer.GetLayerDefn())
        geojson_feature.SetGeometry(geometry)
        Geojson_layer.CreateFeature(geojson_feature)
        geojson_feature = None
for feature in Geojson_layer:
    geometry = feature.GetGeometryRef()
    print(geometry)
# layer = dataSource.GetLayer()