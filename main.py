from osgeo import ogr

dxf_file = r"E:\react-naitve project\campus\src\assets\Bahen Indoor building layout\DXF\Drawing1test.dxf"
dxf_driver = ogr.GetDriverByName("DXF")
dxf_dataSource = dxf_driver.Open(dxf_file, 1)
dxf_layer = dxf_dataSource.GetLayer()
for dxf_layer in dxf_dataSource:
    dxf_layer_name = dxf_layer.GetName()
    print(dxf_layer_name)
for dxf_feature in dxf_layer:
    dxf_geometry = dxf_feature.GetGeometryRef()
    print(dxf_geometry)
# geojson_file = r"E:\react-naitve project\campus\src\assets\Bahen Indoor building layout\DXF\Drawing1test.geojson"
geojson_driver = ogr.GetDriverByName("GeoJSON")
Geojson_dataSource = geojson_driver.CreateDataSource("output.geojson")
Geojson_layer = dxf_dataSource.CopyLayer(dxf_layer, "output")
for feature in Geojson_layer:
    geometry = feature.GetGeometryRef()
    print(geometry)
# layer = dataSource.GetLayer()