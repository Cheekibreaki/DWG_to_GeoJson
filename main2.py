from osgeo import ogr
import collections


def findFeatureForLabel (label_geometry,roomNUM,store_info):
    
    dxf_file = r"E:\react-naitve project\campus\src\assets\Bahen Indoor building layout\DXF\Drawing1test.dxf"
    dxf_driver = ogr.GetDriverByName("DXF")
    dxf_dataSource = dxf_driver.Open(dxf_file, 1)
    
    # # Create a new DXF dataset
    # new_dxf_driver = ogr.GetDriverByName("DXF")
    # new_dxf_dataSource = new_dxf_driver.CreateDataSource(new_dxf_file)

    # # Copy the features from the original layer to the new dataset
    # new_layer_name = "Copy of " + layer_name
    # new_layer = new_dxf_dataSource.CopyLayer(dxf_layer, new_layer_name)

    # # Clean up and close the new dataset
    for dxf_layer in dxf_dataSource:
        for feature in dxf_layer:
            geometry = feature.GetGeometryRef()
            type = geometry.GetGeometryType()
            type_str = ogr.GeometryTypeToName(type)
            # print(type_str)
            if(type_str == "Line String"):
                # print("find feature for label")
                xmin, xmax, ymin, ymax = geometry.GetEnvelope() 
                
                if(xmax > label_geometry.GetX() > xmin and
                    ymin < label_geometry.GetY() < ymax):
                    # feature = ogr.Feature(geojson_layer.GetLayerDefn())
                    # feature.SetField("room", roomNUM)
                    store_info[feature.GetFID()] = roomNUM
                    dxf_dataSource = None
                    return  feature.GetFID()
    dxf_dataSource = None
    return None
           
        

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

    field_defn = ogr.FieldDefn( "room", ogr.OFTString )
    field_defn.SetWidth( 32 )
    geojson_layer.CreateField ( field_defn )

    feature_with_label = {}

    #look for any label exist in the dxf file first and then record them
    for feature in dxf_layer:
        text_value = feature.GetFieldAsString("Text") 
        geometry = feature.GetGeometryRef()
        type = geometry.GetGeometryType()
        type_str = ogr.GeometryTypeToName(type)
        if(type_str == "3D Point"): 
            featureIDIncludeLabel = findFeatureForLabel(geometry,text_value, feature_with_label)
            if(featureIDIncludeLabel != None):
                print("Feature ID include label is ", featureIDIncludeLabel)

    # Loop through the features in the current layer and convert them to GeoJSON
    for feature in dxf_layer:
        feature_id = feature.GetFID()
        print("Feature ID:", feature_id)

        text_value = feature.GetFieldAsString("Text")
        print("Text Value:", text_value)
        
        geometry = feature.GetGeometryRef()
        type = geometry.GetGeometryType()
        type_str = ogr.GeometryTypeToName(type)
        print("typestr:", type_str)
        if(type_str != "3D Point"):

            geojson_feature = ogr.Feature(geojson_layer.GetLayerDefn())
            geojson_feature.SetField("room", "foo")
            for featureID,roomID in feature_with_label.items():
                if(featureID == feature.GetFID()):
                    geojson_feature.SetField("room", roomID)  
                    break
            geojson_feature.SetGeometry(geometry)                      
            geojson_layer.CreateFeature(geojson_feature)

        geojson_feature = None



        

    # featureIDIncludeLabel = findFeatureForLabel(label_geometry,dxf_layer)

    # Clean up and close the data sources for the current layer
geojson_dataSource = None
    # print(geojson_layer.GetFeature(0))
# Clean up and close the data source for the DXF file
dxf_dataSource = None