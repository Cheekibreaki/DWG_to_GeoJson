from osgeo import ogr

dxf_file = r"E:\react-naitve project\campus\src\assets\Bahen Indoor building layout\DXF\Drawing1test.dxf"
driver = ogr.GetDriverByName("DXF")
dataSource = driver.Open(dxf_file, 0)
layer = dataSource.GetLayer()
for feature in layer:
    geometry = feature.GetGeometryRef()
    print(geometry)
# layer = dataSource.GetLayer()