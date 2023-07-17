from osgeo import ogr
import collections
from osgeo import ogr, osr
import math

reference_lat = 43.66001549439409
reference_lon = -79.39736438779232


# def calculate_destination_point(lat1, lon1, d, tc):
#     lat1 = math.radians(lat1)
#     lon1 = math.radians(lon1)
#     tc = math.radians(tc)
#     d = math.radians(d)
    
#     lat = math.degrees(math.asin(math.sin(lat1) * math.cos(d) + math.cos(lat1) * math.sin(d) * math.cos(tc)))
    
#     if math.cos(math.radians(lat)) == 0:
#         lon = lon1  # endpoint at a pole
#     else:
#         lon = (lon1 - math.asin(math.sin(tc) * math.sin(d) / math.cos(math.radians(lat))) + math.pi) % (2 * math.pi) - math.pi
    
#     return math.degrees(lat), math.degrees(lon)

def convert_meters_to_latlon2(x, y, reference_lat, reference_lon):
    ref_utm_x, ref_utm_y = latlon_to_utm(reference_lat,reference_lon)
    result_utm_x = ref_utm_x + x
    result_utm_y = ref_utm_y - y
    result_lat,result_lon = utm_to_latlon(result_utm_x, result_utm_y, 17, northern_hemisphere=True)
    print(result_lat,result_lon)
    return result_lon,result_lat
    
def latlon_to_utm(lat, lon):
    # Create a spatial reference object for WGS84 (EPSG:4326)
    wgs84_srs = osr.SpatialReference()
    wgs84_srs.ImportFromEPSG(4326)

    # Create a spatial reference object for UTM (EPSG:326XX, where XX is the UTM zone)
    utm_srs = osr.SpatialReference()
    utm_srs.SetUTM(17, True)  # Example: UTM zone 1 in the northern hemisphere
    # utm_srs.SetUTM(1, False)  # Example: UTM zone 1 in the southern hemisphere

    # Create a coordinate transformation object
    transform = osr.CoordinateTransformation(wgs84_srs, utm_srs)

    # Transform the lat/lon coordinates to UTM
    utm_x, utm_y, _ = transform.TransformPoint(lon, lat)

    return utm_x, utm_y

def utm_to_latlon(utm_x, utm_y, utm_zone_number, northern_hemisphere=True):
    # Create a spatial reference object for UTM (EPSG:326XX, where XX is the UTM zone)
    utm_srs = osr.SpatialReference()
    utm_srs.SetUTM(utm_zone_number, northern_hemisphere)

    # Create a spatial reference object for WGS84 (EPSG:4326)
    wgs84_srs = osr.SpatialReference()
    wgs84_srs.ImportFromEPSG(4326)

    # Create a coordinate transformation object
    transform = osr.CoordinateTransformation(utm_srs, wgs84_srs)

    # Transform the UTM coordinates to lat/lon
    lon, lat, _ = transform.TransformPoint(utm_x, utm_y)

    return lat, lon




def convert_meters_to_latlon(x, y, reference_lat, reference_lon):
    # Create a source spatial reference in the meter-based coordinate system
    source_srs = osr.SpatialReference()
    source_srs.ImportFromEPSG(32617)  # UTM zone 17N
    source_srs.SetLinearUnits("meter", 1.0)
    # Create a target spatial reference in the geographic coordinate system (e.g., WGS84)
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(4326)  # EPSG code 4326 represents WGS84 (latitude/longitude)

    # Create a coordinate transformation object
    transform = osr.CoordinateTransformation(source_srs, target_srs)

    # Transform the coordinates from meters to latitude/longitude
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(x, y)
    point.Transform(transform)

    # Get the transformed latitude and longitude
    lat = point.GetY()
    print("lat",lat)
    lon = point.GetX()
    print("lon",lon)
    # Adjust the transformed coordinates based on the reference point

    lat -= reference_lat
    lon += reference_lon

    return lat, lon





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

            coords = geometry.GetPoints()
            print(coords)
            
            for i in range(len(coords)):
                #result=calculate_destination_point(reference_lat, reference_lon, math.sqrt(coords[i][0]**2 + coords[i][1]**2) , math.degrees(math.atan2(coords[i][1], coords[i][0])))
                result=convert_meters_to_latlon2(coords[i][0], coords[i][1], reference_lat, reference_lon)
                print(result)
                geometry.SetPoint_2D(i,result[0],result[1])
            geojson_feature.SetGeometry(geometry)                      
            geojson_layer.CreateFeature(geojson_feature)

        geojson_feature = None



        

    # featureIDIncludeLabel = findFeatureForLabel(label_geometry,dxf_layer)

    # Clean up and close the data sources for the current layer
geojson_dataSource = None
    # print(geojson_layer.GetFeature(0))
# Clean up and close the data source for the DXF file
dxf_dataSource = None