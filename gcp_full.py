from qgis.processing import alg
from qgis.core import QgsFeature, QgsFeatureSink

"""

"""
"""

"""


import processing
 
@alg(name="gcpfull", label=alg.tr("GCP Grouping"), group="vds",
     group_label=alg.tr("VDS"))

@alg.input(type=alg.VECTOR_LAYER, name="IMAGE", label="Input images")
@alg.input(type=alg.FIELD, name="IMAGE_FIELD", label="Image file name",
           parentLayerParameterName="IMAGE")

@alg.input(type=alg.VECTOR_LAYER, name="GCP", label="Input GCPs")
@alg.input(type=alg.FIELD, name="GCP_FIELD", label="Name of GCP",
           parentLayerParameterName="GCP")

@alg.input(type=alg.CRS, name="LOCAL_CRS", label="CRS for processing GCPs", 
           default="EPSG:2256")
@alg.input(type=alg.DISTANCE, name="BUFFER_DIST", label="Radius of GCP buffer",
           parentParameterName="LOCAL_CRS", default=10)

@alg.input(type=alg.VECTOR_LAYER_DEST, name="BUFFER", label="GCP Buffer")
@alg.input(type=alg.VECTOR_LAYER_DEST, name="JOINED", label="Joined Layer")

@alg.input(type=alg.BOOL, name="BOOKMARKS", label="Create Bookmarks",
           default=True)

@alg.input(type=alg.FILE_DEST, name="OUTPUT", label="Output file",
           default="GCP_image.txt")

def testalg(instance, parameters, context, feedback, inputs):
    """
    Description goes here. (Don't delete this! Removing this comment will cause errors.)
    """
    img_layer = instance.parameterAsVectorLayer(parameters, "IMAGE", context)
    img_field = instance.parameterAsFields(parameters, "IMAGE_FIELD", context)[0]
    
    gcp_layer = instance.parameterAsVectorLayer(parameters, "GCP", context)
    gcp_field = instance.parameterAsFields(parameters, "GCP_FIELD", context)[0]
    
    local_crs = instance.parameterAsCrs(parameters, "LOCAL_CRS", context)
    
    buffer_dist = instance.parameterAsDouble(parameters, "BUFFER_DIST", context)
    
    buffer_layer = instance.parameterAsOutputLayer(parameters, "BUFFER", context)
    joined_layer = instance.parameterAsOutputLayer(parameters, "JOINED", context)
    
    create_bookmarks = instance.parameterAsBoolean(parameters, "BOOKMARKS", context)
    
    output_file = instance.parameterAsFileOutput(parameters, "OUTPUT", context)
    
    # Reproject gcps
    feedback.pushInfo('Reprojecting GCP layer')
    gcp_layer_reprojected = processing.run("qgis:reprojectlayer", {
        'INPUT': gcp_layer,
        'TARGET_CRS': local_crs,
        'OUTPUT': 'memory:',
    }, context=context, feedback=feedback)['OUTPUT']
    
    # Create buffer around gcps
    feedback.pushInfo('Creating buffers around GCPs')
    gcp_buffer_layer = processing.run("qgis:buffer", {
        'INPUT': gcp_layer_reprojected,
        'DISTANCE': buffer_dist,
        'OUTPUT': buffer_layer,
    }, context=context, feedback=feedback)['OUTPUT']
    
    # Create spatial index for images
    feedback.pushInfo('Creating spatial index for image layer')
    processing.run("qgis:createspatialindex", {
        'INPUT': img_layer,
    }, context=context, feedback=feedback)
    
    # Join images w/ gcps
    # NOTE: find a way to use an enum for the 'PREDICATE' input instead of hard coding it
    feedback.pushInfo('Joining images with GCP buffer')
    joined_layer = processing.run("qgis:joinattributesbylocation", {
        'INPUT': img_layer,
        'JOIN': gcp_buffer_layer,
        'PREDICATE': [5],
        'DISCARD_NONMATCHING': True,
        'OUTPUT': joined_layer,
    }, context=context, feedback=feedback)['OUTPUT']
    
    # Return joined features under a file
    # Note: make the input fields as parameters instead of hard coding them.
    feedback.pushInfo('Creating batch file of images under points')
    processing.run("script:gcpimage", {
        'INPUT': joined_layer,
        'GCP_FIELD': gcp_field,
        'NAME_FIELD': img_field,
        'OUTPUT': output_file,
    }, context=context, feedback=feedback)
    
    if create_bookmarks:
        # Create a list of bookmarks of the gcps
        # NOTE: bookmark extent is zoomed way far out, fix it
        feedback.pushInfo('Creating bookmarks of gcps')
        output_dest = processing.run("script:gcpbookmark", {
            'INPUT': gcp_buffer_layer,
            'NAME_FIELD': gcp_field,
        }, context=context, feedback=feedback)
    
 
    return {
        "OUTPUT": output_file,
        "BUFFER": gcp_buffer_layer,
        "JOINED": joined_layer,
    }