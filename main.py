from osgeo import ogr
import collections
from osgeo import ogr, osr
import math


dxf_folder_list = [{
    "layer_name" : "BA_Indoor_1",
    "path" : r"E:\react-naitve project\campus\src\assets\Bahen Indoor building layout\Bahen - 1stFloor",
    "reference_lat" : 43.65923740619973,
    "reference_lon" : -79.39784311817914,
    "bearing_diff" : 16.5,
    "x_offset" : -7,
    "y_offset" : -2.5,
    "height" : 30
}]

output_dir = r"E:\react-naitve project\campus\src\assets\geojson\\"

# reference_lat = 43.65923740619973
# reference_lon = -79.39784311817914
# bearing_diff = 16.5
# x_offset = -7
# y_offset = -2.5
# height = 30

# layer_name = "indoor_3d_map"

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







def findFeatureForLabel (dxf_file,label_geometry,roomNUM,store_info):
    
    print(dxf_file)
    dxf_driver = ogr.GetDriverByName("DXF")
    dxf_dataSource = dxf_driver.Open(dxf_file, 1)


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
           
def writeGeoJson (dxf_file,layer_name,geo_params,isContour):
    reference_lat, reference_lon,  bearing_diff, height, x_offset,y_offset = geo_params       
    print("dxf_file")
    print("dxf_file",dxf_file)
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
        field_defn = ogr.FieldDefn( "height", ogr.OFTInteger )
        field_defn.SetWidth( 32 )
        geojson_layer.CreateField ( field_defn )
        field_defn = ogr.FieldDefn( "base_height", ogr.OFTInteger )
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
                featureIDIncludeLabel = findFeatureForLabel(dxf_file, geometry,text_value, feature_with_label)
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
                    result=calculate_new_coordinates(reference_lat, reference_lon,coords[i][1], coords[i][0],  bearing_diff, height, x_offset,y_offset )
                    print(result)
                    geometry.SetPoint_2D(i,result[0],result[1])
                geojson_feature.SetGeometry(geometry)          
                geojson_feature.SetField("height", height)  
                geojson_feature.SetField("base_height", height)  
                geojson_layer.CreateFeature(geojson_feature)

            geojson_feature = None


        # Clean up and close the data sources for the current layer
    geojson_dataSource = None
        # print(geojson_layer.GetFeature(0))
    # Clean up and close the data source for the DXF file
    dxf_dataSource = None



if __name__ == "__main__":
    for dxf in dxf_folder_list:
        contour_path = dxf["path"]+"\Contour.dxf"
        room_path = dxf["path"]+"\Room.dxf"
        contour_layer_name = dxf["layer_name"]+"_contour"
        room_layer_name = dxf["layer_name"]+"_room"
        writeGeoJson(room_path,room_layer_name,[dxf["reference_lat"],dxf["reference_lon"],dxf["bearing_diff"],dxf["height"],dxf["x_offset"],dxf["y_offset"]])
        writeGeoJson(contour_path,contour_layer_name,[dxf["reference_lat"],dxf["reference_lon"],dxf["bearing_diff"],dxf["height"],dxf["x_offset"],dxf["y_offset"]])
        
        