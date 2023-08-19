from osgeo import ogr
import collections
from osgeo import ogr, osr
import os
import math
import json

dxf_folder_list = \
[{
    "layer_name" : "BA_Indoor_1",
    "floor" : 1 ,
    "contour_color" : [148, 148, 148] ,
    "room_color" : [255, 225, 143] ,
    "path" : r"E:\react-naitve project\campus\src\assets\Bahen Indoor building layout\Bahen - 1stFloor",
    "reference_lat" : 43.65923740619973,
    "reference_lon" : -79.39784311817914,
    "bearing_diff" : 16.5,
    "x_offset" : -20,
    "y_offset" : -2.5,
    "height" : 0
},{
    "layer_name" : "BA_Indoor_2",
    "floor" : 2 ,
    "contour_color" : [148, 148, 148] ,
    "room_color" : [255, 225, 143] ,
    "path" : r"E:\react-naitve project\campus\src\assets\Bahen Indoor building layout\Bahen - 2ndFloor",
    "reference_lat" : 43.65923740619973,
    "reference_lon" : -79.39784311817914,
    "bearing_diff" : 16.5,
    "x_offset" : -20.5,
    "y_offset" : -26,
    "height" : 50
}]

all_building_json = "all_building"

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


def findFeatureForLabel(dxf_file, label_geometry, roomNUM, store_info):
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
            if (type_str == "Line String"):
                coords = []
                for i in range(geometry.GetPointCount()):
                    coords.append(geometry.GetPoint_2D(i))

                polygon = ogr.Geometry(ogr.wkbPolygon)
                linear_ring = ogr.Geometry(ogr.wkbLinearRing)

                for coord in coords:
                    linear_ring.AddPoint_2D(*coord)

                linear_ring.CloseRings()
                polygon.AddGeometry(linear_ring)

                # print("find feature for label")
                xmin, xmax, ymin, ymax = geometry.GetEnvelope()

                # if (xmax > label_geometry.GetX() > xmin and
                #         ymin < label_geometry.GetY() < ymax):
                #     # feature = ogr.Feature(geojson_layer.GetLayerDefn())
                #     # feature.SetField("room", roomNUM)
                #     store_info[feature.GetFID()] = roomNUM
                #     dxf_dataSource = None
                #     return feature.GetFID()
                if label_geometry.Within(polygon):
                    store_info[feature.GetFID()] = roomNUM
                    dxf_dataSource = None
                    return feature.GetFID()

    dxf_dataSource = None
    return None







# def findFeatureForLabel (dxf_file,label_geometry,roomNUM,store_info):
#
#     print(dxf_file)
#     dxf_driver = ogr.GetDriverByName("DXF")
#     dxf_dataSource = dxf_driver.Open(dxf_file, 1)
#
#
#     # # Clean up and close the new dataset
#     for dxf_layer in dxf_dataSource:
#         for feature in dxf_layer:
#             geometry = feature.GetGeometryRef()
#             type = geometry.GetGeometryType()
#             type_str = ogr.GeometryTypeToName(type)
#             # print(type_str)
#             if(type_str == "Line String"):
#                 # print("find feature for label")
#                 xmin, xmax, ymin, ymax = geometry.GetEnvelope()
#
#                 if(xmax > label_geometry.GetX() > xmin and
#                     ymin < label_geometry.GetY() < ymax):
#                     # feature = ogr.Feature(geojson_layer.GetLayerDefn())
#                     # feature.SetField("room", roomNUM)
#                     store_info[feature.GetFID()] = roomNUM
#                     dxf_dataSource = None
#                     return  feature.GetFID()
#     dxf_dataSource = None
#     return None
           
def writeGeoJson (dxf_file,layer_name,floor_num,color,geo_params,is_all_building):

    reference_lat, reference_lon,  bearing_diff, height, x_offset,y_offset = geo_params       
    print("dxf_file")
    print("dxf_file",dxf_file)
    dxf_driver = ogr.GetDriverByName("DXF")
    dxf_dataSource = dxf_driver.Open(dxf_file, 1)
    print(dxf_dataSource)
    for dxf_layer in dxf_dataSource:
        print(layer_name)
        if(is_all_building):
            output_geojson = output_dir + all_building_json + ".json"
        else:
            output_geojson = output_dir + layer_name + ".json"
        print(output_geojson)
        # Create a new GeoJSON file for the current layer
        geojson_driver = ogr.GetDriverByName("GeoJSON")
        json_is_exist = False
        if os.path.exists(output_geojson):
            json_is_exist = True
        if json_is_exist:
            geojson_dataSource = geojson_driver.Open(output_geojson, 1)
        else:
            geojson_dataSource = geojson_driver.CreateDataSource(output_geojson)

        # Create a new layer in the GeoJSON file
        geojson_layer = geojson_dataSource.CreateLayer(layer_name, geom_type=ogr.wkbUnknown)

        if not json_is_exist:
            field_defn = ogr.FieldDefn( "room", ogr.OFTString )
            field_defn.SetWidth( 32 )
            geojson_layer.CreateField(field_defn)
            field_defn = ogr.FieldDefn("floor", ogr.OFTString)
            field_defn.SetWidth(32)
            geojson_layer.CreateField(field_defn)
            field_defn = ogr.FieldDefn("color", ogr.OFTString)
            field_defn.SetWidth(32)
            geojson_layer.CreateField(field_defn)
            field_defn = ogr.FieldDefn("layer_name", ogr.OFTString)
            field_defn.SetWidth(32)
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
                geojson_feature.SetField("room", "")
                for featureID,roomID in feature_with_label.items():
                    if(featureID == feature.GetFID()):
                        geojson_feature.SetField("room", str.upper(roomID))
                        break

                coords = geometry.GetPoints()
                print(coords)
                
                for i in range(len(coords)):
                    #result=calculate_destination_point(reference_lat, reference_lon, math.sqrt(coords[i][0]**2 + coords[i][1]**2) , math.degrees(math.atan2(coords[i][1], coords[i][0])))
                    result=calculate_new_coordinates(reference_lat, reference_lon,coords[i][1], coords[i][0],  bearing_diff, height, x_offset,y_offset )
                    print(result)
                    geometry.SetPoint_2D(i,result[0],result[1])

                coords = []
                for i in range(geometry.GetPointCount()):
                    coords.append(geometry.GetPoint_2D(i))

                polygon = ogr.Geometry(ogr.wkbPolygon)
                linear_ring = ogr.Geometry(ogr.wkbLinearRing)

                for coord in coords:
                    linear_ring.AddPoint_2D(*coord)

                linear_ring.CloseRings()
                polygon.AddGeometry(linear_ring)

                geojson_feature.SetGeometry(polygon)
                geojson_feature.SetField("layer_name", layer_name)
                geojson_feature.SetField("height", height)
                geojson_feature.SetField("base_height", height)
                geojson_feature.SetField("color", str(color))
                geojson_feature.SetField("floor", floor_num)
                geojson_layer.CreateFeature(geojson_feature)



            geojson_feature = None
        geojson_dataSource = None

        # Clean up and close the data sources for the current layer
    geojson_dataSource = None
        # print(geojson_layer.GetFeature(0))
    # Clean up and close the data source for the DXF file
    dxf_dataSource = None


def combine_json_files(input_files, output_file):
    combined_data = []
    for file_path in input_files:
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)  # Load JSON data from file into a Python dictionary
                print("data",data["features"][0])
                for feature in data["features"]:
                    combined_data.append(feature)
                # combined_data.update(data)  # Merge dictionaries
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error processing file '{file_path}': {e}")
    json_content = {"features":combined_data, "type": "FeatureCollection"}

    with open(output_file, 'w') as outfile:
        json.dump(json_content, outfile, indent=2)  # Use indent for pretty formatting


if __name__ == "__main__":
    try:
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
    except OSError as e:
        print(f"Error: {e}")



    for dxf in dxf_folder_list:
        contour_path = dxf["path"]+"\Contour.dxf"
        room_path = dxf["path"]+"\Room.dxf"
        contour_layer_name = dxf["layer_name"]+"_contour"
        room_layer_name = dxf["layer_name"]+"_room"
        room_color = dxf["room_color"]
        contour_color = dxf["contour_color"]
        floor_num = dxf["floor"]
        writeGeoJson(room_path,room_layer_name,floor_num,room_color,[dxf["reference_lat"],dxf["reference_lon"],dxf["bearing_diff"],dxf["height"]+1,dxf["x_offset"],dxf["y_offset"]],False)
        writeGeoJson(contour_path,contour_layer_name,floor_num,contour_color,[dxf["reference_lat"],dxf["reference_lon"],dxf["bearing_diff"],dxf["height"],dxf["x_offset"],dxf["y_offset"]],False)

    input_files = []
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        input_files.append(file_path)
    print("input",input_files)
    combine_json_files(input_files,output_dir + all_building_json + ".json")
        