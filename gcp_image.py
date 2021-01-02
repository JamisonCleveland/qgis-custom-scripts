from qgis.processing import alg
 
import itertools
 
@alg(name="gcpimage", label=alg.tr("GCP Image"), group="vds",
     group_label=alg.tr("VDS"))
@alg.input(type=alg.SOURCE, name="INPUT", label="Input layer")
@alg.input(type=alg.FIELD, name="GCP_FIELD", label="GCP number field",
           parentLayerParameterName="INPUT")
@alg.input(type=alg.FIELD, name="NAME_FIELD", label="Image name field",
           parentLayerParameterName="INPUT")
@alg.input(type=alg.FILE_DEST, name="OUTPUT",
           label="Name and path of the output")
def gcp_image(instance, parameters, context, feedback, inputs):
    """
    Creates a batch file of image file names, given a layer of joined features
    """
    
    source = instance.parameterAsSource(parameters, "INPUT", context)
    
    gcp_field = instance.parameterAsFields(parameters, "GCP_FIELD", context)[0]
    name_field = instance.parameterAsFields(parameters, "NAME_FIELD", context)[0]
    
    file_destination = instance.parameterAsFile(parameters, "OUTPUT", context)
    
    features = sorted(source.getFeatures(), key=lambda a: a[gcp_field])
    grouped_features = itertools.groupby(features, key=lambda a: a[gcp_field])
    
    total = 100.0 / source.featureCount() if source.featureCount() else 0
    current = 0
    
    with open(file_destination, 'w') as output_images:
        for gcp_name, feature_group in grouped_features:
            if feedback.isCanceled():
                break
            
            image_batch = [
                f'\"{feature[name_field]}\"' for feature in feature_group
            ]
            
            if not isinstance(gcp_name, str):
                gcp_name = f'GCP_{gcp_name}'
            
            output_images.write(gcp_name + '\n' + ' '.join(image_batch) + '\n\n')
            
            feedback.setProgress(int(current * total))
            current += len(image_batch)
    
    return {"OUTPUT": file_destination}