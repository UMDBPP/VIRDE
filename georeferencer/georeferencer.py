'''
Created on Jul 20, 2017

@author: Zach
'''

import os

input_dir = 'B:/Workspaces/QGIS/VIRDE/NS67/tiff/'
output_dir = 'B:/Workspaces/QGIS/VIRDE/NS67/geotiff/'

input_csv = 'B:/Workspaces/R/VIRDE/georeference.csv'
output_script_file = 'B:/Workspaces/Python/VIRDE/georeferencer/georeferencer.bat'


with open(output_script_file, 'w') as output_script:
    for row in open(input_csv, 'r').readlines():
        row_data = row.replace(' ', '').replace('"', '').replace('\n', '').split(',')
        image_path = input_dir + row_data[1]
        if os.path.isfile(image_path) and 'NA' not in row_data:
            output_string = os.path.join('A:\\', 'OSGeo4W64', 'bin', 'gdal_translate.exe') + ' -of GTiff -a_srs EPSG:4326 '
            output_string += '-gcp 0 0 %s %s ' % (row_data[9], row_data[10])
            output_string += '-gcp 3296 0 %s %s ' % (row_data[11], row_data[12])
            output_string += '-gcp 0 2464 %s %s ' % (row_data[13], row_data[14])
            output_string += '-gcp 3296 2464 %s %s ' % (row_data[15], row_data[16])
            output_string += '"%s" "%s" \n' % (image_path, output_dir + row_data[1])
            output_script.write(output_string)
