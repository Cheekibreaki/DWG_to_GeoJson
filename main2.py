from osgeo import ogr
import collections
from osgeo import ogr, osr
import math


reference_lat = 43.65923740619973
reference_lon = -79.39784311817914
bearing_diff = 16.5
x_offset = -8
y_offset = -2.5
height = 0

layer_name = "indoor_3d_map"

from geopy.distance import distance#, VincentyDistance
from geopy.point import Point


def calculate_new_coordinates(latitude, longitude, x, y,bearing_diff, height, x_offset,y_offset):
    y = y+y_offset
    x = x+x_offset
    length = math.sqrt(y**2 + x**2)
    bearing = math.atan2(y, x)
    bearing_degrees = math.degrees(bearing)
    
    # Create a Point object with the original coordinates
    original_point = Point(latitude, longitude)

    # Calculate the distance to move (100 meters)
    distance_to_move = distance(meters=length)

    # Use the destination method to get the new coordinates
    new_point = distance_to_move.destination(point=original_point, bearing=bearing_degrees-bearing_diff)

    # Extract the latitude and longitude from the new point
    new_latitude, new_longitude = new_point.latitude, new_point.longitude

    return new_longitude,new_latitude



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
output_dir = r"E:\react-naitve project\campus\src\assets\\"
dxf_driver = ogr.GetDriverByName("DXF")
dxf_dataSource = dxf_driver.Open(dxf_file, 1)
print(dxf_dataSource)
for dxf_layer in dxf_dataSource:
    print(layer_name)
    output_geojson = output_dir + layer_name + ".json"
    print(output_geojson)
    # Create a new GeoJSON file for the current layer
    geojson_driver = ogr.GetDriverByName("GeoJSON")
    geojson_dataSource = geojson_driver.CreateDataSource(output_geojson)

    # Create a new layer in the GeoJSON file
    geojson_layer = geojson_dataSource.CreateLayer(layer_name, geom_type=ogr.wkbUnknown)

    field_defn = ogr.FieldDefn( "room", ogr.OFTString )
    field_defn.SetWidth( 32 )
    geojson_layer.CreateField ( field_defn )
    field_defn = ogr.FieldDefn( "height", ogr.OFTString )
    field_defn.SetWidth( 32 )
    geojson_layer.CreateField ( field_defn )
    field_defn = ogr.FieldDefn( "base_height", ogr.OFTString )
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
            geojson_feature.SetField("room", "unknown")
            for featureID,roomID in feature_with_label.items():
                if(featureID == feature.GetFID()):
                    geojson_feature.SetField("room", roomID)  
                    break

            coords = geometry.GetPoints()
            print(coords)
            
            for i in range(len(coords)):
                #result=calculate_destination_point(reference_lat, reference_lon, math.sqrt(coords[i][0]**2 + coords[i][1]**2) , math.degrees(math.atan2(coords[i][1], coords[i][0])))
                result=calculate_new_coordinates(reference_lat, reference_lon,coords[i][1], coords[i][0], bearing_diff, x_offset,y_offset ,height)
                print(result)
                geometry.SetPoint_2D(i,result[0],result[1])
            geojson_feature.SetGeometry(geometry)          
            geojson_feature.SetField("height", height)  
            geojson_feature.SetField("base_height", height)  
            geojson_layer.CreateFeature(geojson_feature)

        geojson_feature = None



        

    # featureIDIncludeLabel = findFeatureForLabel(label_geometry,dxf_layer)

    # Clean up and close the data sources for the current layer
geojson_dataSource = None
    # print(geojson_layer.GetFeature(0))
# Clean up and close the data source for the DXF file
dxf_dataSource = None