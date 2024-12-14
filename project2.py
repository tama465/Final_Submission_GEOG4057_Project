import arcpy
import os
import ee
import pandas as pd

"""
example usage: python project2.py D:\project2 boundary.csv pnt_elev2.shp 32119
"""



def getGeeElevation(workspace,csv_file,outfc_name, epsg=4326):
    """
    workspace= directory that contains input and output
    csv_file= input csv file name
    epsg = wkid code for spatial reference e.g 4326 WGS GCS
    """

    # Load the CSV
    csv_file = os.path.join(workspace,csv_file)  # Replace with your CSV file path
    df = pd.read_csv(csv_file)
    dem = ee.Image('USGS/3DEP/10m')
    geometrys = [ee.Geometry.Point([x,y],f'EPSG:{epsg}') for x,y in zip(df['X'], df['Y'])]
    fc = ee.FeatureCollection(geometrys)
    original_info = fc.getInfo()
    sampled_fc = dem.sampleRegions(
        collection=fc,
        scale=10, 
        geometries=True 
    )
    sampled_info = sampled_fc.getInfo()
    for ind, itm in enumerate(original_info['features']):
        itm['properties']= sampled_info['features'][ind]['properties']
 
    fcname= os.path.join(workspace, outfc_name)
    if arcpy.Exists(fcname):
        arcpy.management.Delete(fcname)
    arcpy.management.CreateFeatureclass(workspace, outfc_name, geometry_type='POINT', spatial_reference=epsg)
    arcpy.management.AddField(fcname, field_name='elevation', field_type='FLOAT')
    with arcpy.da.InsertCursor(fcname, ['SHAPE@','elevation']) as cursor:
        for feat in original_info['features']:
            # get the coordiantes and create pointgeometry
            coords= feat['geometry']['coordinates']
            pnt= arcpy.PointGeometry(arcpy.Point(coords[0],coords[1]), spatial_reference=32119)
            # get the properties and write it to the 'elevation'
            elev = feat['properties']['elevation']
            cursor.insertRow([pnt, elev])
        



def main():
    import sys
    try:
        ee.Initialize()
    except:
        ee.Authenticate()
        ee.Initialize()
    workspace = sys.argv[1]
    csv_file = sys.argv[2]
    outfc_name = sys.argv[3]
    epsg = int(sys.argv[4])
    getGeeElevation(workspace= workspace,csv_file=csv_file, outfc_name=outfc_name, epsg=epsg)



if __name__ == '__main__':
    main()