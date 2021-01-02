from qgis.processing import alg
from qgis.core import (QgsProject, QgsReferencedRectangle, QgsBookmark)
 
@alg(name="gcpbookmark", label=alg.tr("GCP Bookmark"), group="vds",
     group_label=alg.tr("VDS"))
@alg.input(type=alg.SOURCE, name="INPUT", label="Input layer")
@alg.input(type=alg.FIELD, name="NAME_FIELD", label="Name field",
           parentLayerParameterName="INPUT")
@alg.output(type=alg.INT, name="OUTPUT", label="Number of bookmarks made")
def gcp_bookmark(instance, parameters, context, feedback, inputs):
    """
    Creates a bookmark for the location of each GCP, given the GCP's buffer.
    """
    source = instance.parameterAsSource(parameters, "INPUT", context)
    
    name_field = instance.parameterAsFields(parameters, "NAME_FIELD", context)[0]
    
    bookmark_manager = QgsProject.instance().bookmarkManager()
    coord = source.sourceCrs()
 
    total = 100.0 / source.featureCount() if source.featureCount() else 0
    features = source.getFeatures()
    for current, feature in enumerate(features):
        if feedback.isCanceled():
            break
        
        # Instead of getting the name from an attribute, 
        # this gets the feature's id and turns it into the gcp name.
        gcp_name = str(feature[name_field])
        gcp_view = feature.geometry().boundingBox()
        
        bookmark = QgsBookmark()
        bookmark.setName(gcp_name)
        bookmark.setExtent(QgsReferencedRectangle(gcp_view, coord))

        
        bookmark_manager.addBookmark(bookmark)
        
        feedback.setProgress(int(current * total))
 
    return {"OUTPUT": source.featureCount()}