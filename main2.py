from osgeo import ogr

dxf_file = r"E:\react-naitve project\campus\src\assets\Bahen Indoor building layout\DXF\Drawing1test.dxf"
output_dir = r"E:\react-naitve project\campus\src\assets\Bahen Indoor building layout\DXF\\"
dxf_driver = ogr.GetDriverByName("DXF")
dxf_dataSource = dxf_driver.Open(dxf_file, 1)
print(dxf_dataSource)
for dxf_layer in dxf_dataSource:
    layer_name = dxf_layer.GetName()
    print(layer_name)
    output_geojson = output_dir + layer_name + ".geojson"
    print(output_geojson)
    # Create a new GeoJSON file for the current layer
    geojson_driver = ogr.GetDriverByName("GeoJSON")
    geojson_dataSource = geojson_driver.CreateDataSource(output_geojson)

    # Create a new layer in the GeoJSON file
    geojson_layer = geojson_dataSource.CreateLayer(layer_name, geom_type=ogr.wkbUnknown)

    # Loop through the features in the current layer and convert them to GeoJSON
    for feature in dxf_layer:
        feature_id = feature.GetFID()
        print("Feature ID:", feature_id)

        text_value = feature.GetFieldAsString("Text")
        print("Text Value:", text_value)

        geometry = feature.GetGeometryRef()
        geojson_feature = ogr.Feature(geojson_layer.GetLayerDefn())
        geojson_feature.SetGeometry(geometry)
        geojson_layer.CreateFeature(geojson_feature)
        
        geojson_feature = None

    # Clean up and close the data sources for the current layer
    geojson_dataSource = None
    # print(geojson_layer.GetFeature(0))
# Clean up and close the data source for the DXF file
dataSource = None