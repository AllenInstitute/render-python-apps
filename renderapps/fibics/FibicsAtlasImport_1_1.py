# /nas/ATLASimport/FibicsAtlasImport_1_1.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:e92452c8d3e28a9e27abfc9994d2007779e7f4c9
# Generated 2017-10-03 14:48:32.252204 by PyXB version 1.2.5 using Python 2.7.12.final.0
# Namespace AbsentNamespace0

from __future__ import unicode_literals
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import io
import pyxb.utils.utility
import pyxb.utils.domutils
import sys
import pyxb.utils.six as _six
# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:996c232a-a884-11e7-b530-a0369f3e81b8')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.5'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

# A holder for module-level binding classes so we can access them from
# inside class definitions where property names may conflict.
_module_typeBindings = pyxb.utils.utility.Object()

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.CreateAbsentNamespace()
Namespace.configureCategories(['typeBinding', 'elementBinding'])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.

    @param xml_text An XML document.  This should be data (Python 2
    str or Python 3 bytes), or a text (Python 2 unicode or Python 3
    str) in the L{pyxb._InputEncoding} encoding.

    @keyword default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utils.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement, default_namespace=default_namespace)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    xmld = xml_text
    if isinstance(xmld, _six.text_type):
        xmld = xmld.encode(pyxb._InputEncoding)
    saxer.parse(io.BytesIO(xmld))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, default_namespace)


# Atomic simple type: [anonymous]
class STD_ANON (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 160, 5)
    _Documentation = None
STD_ANON._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON, enum_prefix=None)
STD_ANON.Oval = STD_ANON._CF_enumeration.addEnumeration(unicode_value='Oval', tag='Oval')
STD_ANON.Polygon = STD_ANON._CF_enumeration.addEnumeration(unicode_value='Polygon', tag='Polygon')
STD_ANON.Rectangle = STD_ANON._CF_enumeration.addEnumeration(unicode_value='Rectangle', tag='Rectangle')
STD_ANON._InitializeFacetMap(STD_ANON._CF_enumeration)
_module_typeBindings.STD_ANON = STD_ANON

# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    """All items to be imported are contained in this node.  acquired data (datasets, images and mosaics) will be placed in the imported date section of the project exaclty as they are structured in this file."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 8, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element DataSet uses Python identifier DataSet
    __DataSet = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'DataSet'), 'DataSet', '__AbsentNamespace0_CTD_ANON_DataSet', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 32, 1), )

    
    DataSet = property(__DataSet.value, __DataSet.set, None, 'Collection of data that has been aquired and is to be imported.')

    
    # Element PlaceableImage uses Python identifier PlaceableImage
    __PlaceableImage = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'PlaceableImage'), 'PlaceableImage', '__AbsentNamespace0_CTD_ANON_PlaceableImage', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 46, 1), )

    
    PlaceableImage = property(__PlaceableImage.value, __PlaceableImage.set, None, 'Representation of Image on disk. Which could be actually Two files for two channels.  Images that are imported at thr root level or in Datasets will be individually outlined and selectable in the Atlas project.')

    
    # Element SectionSet uses Python identifier SectionSet
    __SectionSet = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'SectionSet'), 'SectionSet', '__AbsentNamespace0_CTD_ANON_SectionSet', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 65, 1), )

    
    SectionSet = property(__SectionSet.value, __SectionSet.set, None, 'A collection of Sections that define a group of regions')

    
    # Element AtlasRegion uses Python identifier AtlasRegion
    __AtlasRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'AtlasRegion'), 'AtlasRegion', '__AbsentNamespace0_CTD_ANON_AtlasRegion', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 89, 1), )

    
    AtlasRegion = property(__AtlasRegion.value, __AtlasRegion.set, None, 'A geo that describes an area of interest')

    
    # Element ImportMosaic uses Python identifier ImportMosaic
    __ImportMosaic = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ImportMosaic'), 'ImportMosaic', '__AbsentNamespace0_CTD_ANON_ImportMosaic', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 203, 1), )

    
    ImportMosaic = property(__ImportMosaic.value, __ImportMosaic.set, None, 'The spec for an ImportMosaic node is identical to the DataSet node, but it can only contain Images.  The ImportMosaic will be outlined and selectable in Atlas5 at the mosaic level - the individual images will not be individually selectable, alignable, etc.')

    
    # Element PrecisionSiteSpec uses Python identifier PrecisionSiteSpec
    __PrecisionSiteSpec = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'PrecisionSiteSpec'), 'PrecisionSiteSpec', '__AbsentNamespace0_CTD_ANON_PrecisionSiteSpec', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 215, 1), )

    
    PrecisionSiteSpec = property(__PrecisionSiteSpec.value, __PrecisionSiteSpec.set, None, 'For precision sites, an overview, single image is taken, some service provides a correction shift, and a single image high res image is taken using beam shift.  Precision sites are not imported by the regular import process, the Precision Site Automation tool must be used.  The parent transform should just be the position and rotation of the site.')

    
    # Attribute version uses Python identifier version
    __version = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'version'), 'version', '__AbsentNamespace0_CTD_ANON_version', pyxb.binding.datatypes.string, fixed=True, unicode_default='1.1', required=True)
    __version._DeclarationLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 25, 3)
    __version._UseLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 25, 3)
    
    version = property(__version.value, __version.set, None, 'The version string of "1.1" is required.')

    _ElementMap.update({
        __DataSet.name() : __DataSet,
        __PlaceableImage.name() : __PlaceableImage,
        __SectionSet.name() : __SectionSet,
        __AtlasRegion.name() : __AtlasRegion,
        __ImportMosaic.name() : __ImportMosaic,
        __PrecisionSiteSpec.name() : __PrecisionSiteSpec
    })
    _AttributeMap.update({
        __version.name() : __version
    })
_module_typeBindings.CTD_ANON = CTD_ANON


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_ (pyxb.binding.basis.complexTypeDefinition):
    """Collection of data that has been aquired and is to be imported."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 36, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element DataSet uses Python identifier DataSet
    __DataSet = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'DataSet'), 'DataSet', '__AbsentNamespace0_CTD_ANON__DataSet', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 32, 1), )

    
    DataSet = property(__DataSet.value, __DataSet.set, None, 'Collection of data that has been aquired and is to be imported.')

    
    # Element Name uses Python identifier Name
    __Name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Name'), 'Name', '__AbsentNamespace0_CTD_ANON__Name', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 38, 4), )

    
    Name = property(__Name.value, __Name.set, None, None)

    
    # Element PlaceableImage uses Python identifier PlaceableImage
    __PlaceableImage = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'PlaceableImage'), 'PlaceableImage', '__AbsentNamespace0_CTD_ANON__PlaceableImage', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 46, 1), )

    
    PlaceableImage = property(__PlaceableImage.value, __PlaceableImage.set, None, 'Representation of Image on disk. Which could be actually Two files for two channels.  Images that are imported at thr root level or in Datasets will be individually outlined and selectable in the Atlas project.')

    
    # Element ParentTransform uses Python identifier ParentTransform
    __ParentTransform = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), 'ParentTransform', '__AbsentNamespace0_CTD_ANON__ParentTransform', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1), )

    
    ParentTransform = property(__ParentTransform.value, __ParentTransform.set, None, 'A 4X4 Matrix that represent the position, scale and shear of a placeable.')

    
    # Element ImportMosaic uses Python identifier ImportMosaic
    __ImportMosaic = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ImportMosaic'), 'ImportMosaic', '__AbsentNamespace0_CTD_ANON__ImportMosaic', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 203, 1), )

    
    ImportMosaic = property(__ImportMosaic.value, __ImportMosaic.set, None, 'The spec for an ImportMosaic node is identical to the DataSet node, but it can only contain Images.  The ImportMosaic will be outlined and selectable in Atlas5 at the mosaic level - the individual images will not be individually selectable, alignable, etc.')

    _ElementMap.update({
        __DataSet.name() : __DataSet,
        __Name.name() : __Name,
        __PlaceableImage.name() : __PlaceableImage,
        __ParentTransform.name() : __ParentTransform,
        __ImportMosaic.name() : __ImportMosaic
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_ = CTD_ANON_


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    """Representation of Image on disk. Which could be actually Two files for two channels.  Images that are imported at thr root level or in Datasets will be individually outlined and selectable in the Atlas project."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 50, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element Name uses Python identifier Name
    __Name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Name'), 'Name', '__AbsentNamespace0_CTD_ANON_2_Name', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 52, 4), )

    
    Name = property(__Name.value, __Name.set, None, None)

    
    # Element FileName uses Python identifier FileName
    __FileName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'FileName'), 'FileName', '__AbsentNamespace0_CTD_ANON_2_FileName', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 54, 4), )

    
    FileName = property(__FileName.value, __FileName.set, None, None)

    
    # Element Channels uses Python identifier Channels
    __Channels = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Channels'), 'Channels', '__AbsentNamespace0_CTD_ANON_2_Channels', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 55, 4), )

    
    Channels = property(__Channels.value, __Channels.set, None, None)

    
    # Element ParentTransform uses Python identifier ParentTransform
    __ParentTransform = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), 'ParentTransform', '__AbsentNamespace0_CTD_ANON_2_ParentTransform', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1), )

    
    ParentTransform = property(__ParentTransform.value, __ParentTransform.set, None, 'A 4X4 Matrix that represent the position, scale and shear of a placeable.')

    _ElementMap.update({
        __Name.name() : __Name,
        __FileName.name() : __FileName,
        __Channels.name() : __Channels,
        __ParentTransform.name() : __ParentTransform
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_2 = CTD_ANON_2


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_3 (pyxb.binding.basis.complexTypeDefinition):
    """Complex type [anonymous] with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 56, 5)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element Channel uses Python identifier Channel
    __Channel = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Channel'), 'Channel', '__AbsentNamespace0_CTD_ANON_3_Channel', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 142, 1), )

    
    Channel = property(__Channel.value, __Channel.set, None, 'Description of a subpart of an image. It describes the location of the file and what detector it was acquired with.')

    _ElementMap.update({
        __Channel.name() : __Channel
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_3 = CTD_ANON_3


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_4 (pyxb.binding.basis.complexTypeDefinition):
    """A collection of Sections that define a group of regions"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 69, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element Name uses Python identifier Name
    __Name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Name'), 'Name', '__AbsentNamespace0_CTD_ANON_4_Name', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 71, 4), )

    
    Name = property(__Name.value, __Name.set, None, None)

    
    # Element Section uses Python identifier Section
    __Section = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Section'), 'Section', '__AbsentNamespace0_CTD_ANON_4_Section', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 102, 1), )

    
    Section = property(__Section.value, __Section.set, None, 'Special Atlas Region that leaves in a SectionSet as geo representations of individual regions')

    
    # Element ParentTransform uses Python identifier ParentTransform
    __ParentTransform = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), 'ParentTransform', '__AbsentNamespace0_CTD_ANON_4_ParentTransform', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1), )

    
    ParentTransform = property(__ParentTransform.value, __ParentTransform.set, None, 'A 4X4 Matrix that represent the position, scale and shear of a placeable.')

    _ElementMap.update({
        __Name.name() : __Name,
        __Section.name() : __Section,
        __ParentTransform.name() : __ParentTransform
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_4 = CTD_ANON_4


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_5 (pyxb.binding.basis.complexTypeDefinition):
    """A colection of Atlas Regions"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 81, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element Name uses Python identifier Name
    __Name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Name'), 'Name', '__AbsentNamespace0_CTD_ANON_5_Name', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 83, 4), )

    
    Name = property(__Name.value, __Name.set, None, None)

    
    # Element AtlasRegion uses Python identifier AtlasRegion
    __AtlasRegion = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'AtlasRegion'), 'AtlasRegion', '__AbsentNamespace0_CTD_ANON_5_AtlasRegion', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 89, 1), )

    
    AtlasRegion = property(__AtlasRegion.value, __AtlasRegion.set, None, 'A geo that describes an area of interest')

    
    # Element ParentTransform uses Python identifier ParentTransform
    __ParentTransform = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), 'ParentTransform', '__AbsentNamespace0_CTD_ANON_5_ParentTransform', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1), )

    
    ParentTransform = property(__ParentTransform.value, __ParentTransform.set, None, 'A 4X4 Matrix that represent the position, scale and shear of a placeable.')

    _ElementMap.update({
        __Name.name() : __Name,
        __AtlasRegion.name() : __AtlasRegion,
        __ParentTransform.name() : __ParentTransform
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_5 = CTD_ANON_5


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_6 (pyxb.binding.basis.complexTypeDefinition):
    """A geo that describes an area of interest"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 93, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element Name uses Python identifier Name
    __Name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Name'), 'Name', '__AbsentNamespace0_CTD_ANON_6_Name', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 95, 4), )

    
    Name = property(__Name.value, __Name.set, None, None)

    
    # Element RotationCenter uses Python identifier RotationCenter
    __RotationCenter = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'RotationCenter'), 'RotationCenter', '__AbsentNamespace0_CTD_ANON_6_RotationCenter', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 98, 4), )

    
    RotationCenter = property(__RotationCenter.value, __RotationCenter.set, None, None)

    
    # Element ParentTransform uses Python identifier ParentTransform
    __ParentTransform = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), 'ParentTransform', '__AbsentNamespace0_CTD_ANON_6_ParentTransform', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1), )

    
    ParentTransform = property(__ParentTransform.value, __ParentTransform.set, None, 'A 4X4 Matrix that represent the position, scale and shear of a placeable.')

    
    # Element Geometry uses Python identifier Geometry
    __Geometry = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Geometry'), 'Geometry', '__AbsentNamespace0_CTD_ANON_6_Geometry', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 153, 1), )

    
    Geometry = property(__Geometry.value, __Geometry.set, None, 'Representation of a shape supported by Atlas 5. It contains vertices that decribe the shape. Note: Rectangle and Oval are described with X and Y Size. While Polygons are described with Vertex Positions')

    _ElementMap.update({
        __Name.name() : __Name,
        __RotationCenter.name() : __RotationCenter,
        __ParentTransform.name() : __ParentTransform,
        __Geometry.name() : __Geometry
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_6 = CTD_ANON_6


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_7 (pyxb.binding.basis.complexTypeDefinition):
    """Special Atlas Region that leaves in a SectionSet as geo representations of individual regions"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 106, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element Name uses Python identifier Name
    __Name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Name'), 'Name', '__AbsentNamespace0_CTD_ANON_7_Name', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 108, 4), )

    
    Name = property(__Name.value, __Name.set, None, None)

    
    # Element RotationCenter uses Python identifier RotationCenter
    __RotationCenter = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'RotationCenter'), 'RotationCenter', '__AbsentNamespace0_CTD_ANON_7_RotationCenter', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 111, 4), )

    
    RotationCenter = property(__RotationCenter.value, __RotationCenter.set, None, None)

    
    # Element ParentTransform uses Python identifier ParentTransform
    __ParentTransform = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), 'ParentTransform', '__AbsentNamespace0_CTD_ANON_7_ParentTransform', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1), )

    
    ParentTransform = property(__ParentTransform.value, __ParentTransform.set, None, 'A 4X4 Matrix that represent the position, scale and shear of a placeable.')

    
    # Element Geometry uses Python identifier Geometry
    __Geometry = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Geometry'), 'Geometry', '__AbsentNamespace0_CTD_ANON_7_Geometry', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 153, 1), )

    
    Geometry = property(__Geometry.value, __Geometry.set, None, 'Representation of a shape supported by Atlas 5. It contains vertices that decribe the shape. Note: Rectangle and Oval are described with X and Y Size. While Polygons are described with Vertex Positions')

    _ElementMap.update({
        __Name.name() : __Name,
        __RotationCenter.name() : __RotationCenter,
        __ParentTransform.name() : __ParentTransform,
        __Geometry.name() : __Geometry
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_7 = CTD_ANON_7


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_8 (pyxb.binding.basis.complexTypeDefinition):
    """A 4X4 Matrix that represent the position, scale and shear of a placeable."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 119, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element M11 uses Python identifier M11
    __M11 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M11'), 'M11', '__AbsentNamespace0_CTD_ANON_8_M11', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 121, 4), )

    
    M11 = property(__M11.value, __M11.set, None, None)

    
    # Element M12 uses Python identifier M12
    __M12 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M12'), 'M12', '__AbsentNamespace0_CTD_ANON_8_M12', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 122, 4), )

    
    M12 = property(__M12.value, __M12.set, None, None)

    
    # Element M13 uses Python identifier M13
    __M13 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M13'), 'M13', '__AbsentNamespace0_CTD_ANON_8_M13', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 123, 4), )

    
    M13 = property(__M13.value, __M13.set, None, None)

    
    # Element M14 uses Python identifier M14
    __M14 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M14'), 'M14', '__AbsentNamespace0_CTD_ANON_8_M14', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 124, 4), )

    
    M14 = property(__M14.value, __M14.set, None, None)

    
    # Element M21 uses Python identifier M21
    __M21 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M21'), 'M21', '__AbsentNamespace0_CTD_ANON_8_M21', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 125, 4), )

    
    M21 = property(__M21.value, __M21.set, None, None)

    
    # Element M22 uses Python identifier M22
    __M22 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M22'), 'M22', '__AbsentNamespace0_CTD_ANON_8_M22', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 126, 4), )

    
    M22 = property(__M22.value, __M22.set, None, None)

    
    # Element M23 uses Python identifier M23
    __M23 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M23'), 'M23', '__AbsentNamespace0_CTD_ANON_8_M23', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 127, 4), )

    
    M23 = property(__M23.value, __M23.set, None, None)

    
    # Element M24 uses Python identifier M24
    __M24 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M24'), 'M24', '__AbsentNamespace0_CTD_ANON_8_M24', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 128, 4), )

    
    M24 = property(__M24.value, __M24.set, None, None)

    
    # Element M31 uses Python identifier M31
    __M31 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M31'), 'M31', '__AbsentNamespace0_CTD_ANON_8_M31', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 129, 4), )

    
    M31 = property(__M31.value, __M31.set, None, None)

    
    # Element M32 uses Python identifier M32
    __M32 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M32'), 'M32', '__AbsentNamespace0_CTD_ANON_8_M32', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 130, 4), )

    
    M32 = property(__M32.value, __M32.set, None, None)

    
    # Element M33 uses Python identifier M33
    __M33 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M33'), 'M33', '__AbsentNamespace0_CTD_ANON_8_M33', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 131, 4), )

    
    M33 = property(__M33.value, __M33.set, None, None)

    
    # Element M34 uses Python identifier M34
    __M34 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M34'), 'M34', '__AbsentNamespace0_CTD_ANON_8_M34', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 132, 4), )

    
    M34 = property(__M34.value, __M34.set, None, None)

    
    # Element M41 uses Python identifier M41
    __M41 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M41'), 'M41', '__AbsentNamespace0_CTD_ANON_8_M41', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 133, 4), )

    
    M41 = property(__M41.value, __M41.set, None, None)

    
    # Element M42 uses Python identifier M42
    __M42 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M42'), 'M42', '__AbsentNamespace0_CTD_ANON_8_M42', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 134, 4), )

    
    M42 = property(__M42.value, __M42.set, None, None)

    
    # Element M43 uses Python identifier M43
    __M43 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M43'), 'M43', '__AbsentNamespace0_CTD_ANON_8_M43', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 135, 4), )

    
    M43 = property(__M43.value, __M43.set, None, None)

    
    # Element M44 uses Python identifier M44
    __M44 = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'M44'), 'M44', '__AbsentNamespace0_CTD_ANON_8_M44', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 136, 4), )

    
    M44 = property(__M44.value, __M44.set, None, None)

    
    # Element CenterLocalX uses Python identifier CenterLocalX
    __CenterLocalX = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'CenterLocalX'), 'CenterLocalX', '__AbsentNamespace0_CTD_ANON_8_CenterLocalX', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 137, 4), )

    
    CenterLocalX = property(__CenterLocalX.value, __CenterLocalX.set, None, None)

    
    # Element CenterLocalY uses Python identifier CenterLocalY
    __CenterLocalY = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'CenterLocalY'), 'CenterLocalY', '__AbsentNamespace0_CTD_ANON_8_CenterLocalY', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 138, 4), )

    
    CenterLocalY = property(__CenterLocalY.value, __CenterLocalY.set, None, None)

    _ElementMap.update({
        __M11.name() : __M11,
        __M12.name() : __M12,
        __M13.name() : __M13,
        __M14.name() : __M14,
        __M21.name() : __M21,
        __M22.name() : __M22,
        __M23.name() : __M23,
        __M24.name() : __M24,
        __M31.name() : __M31,
        __M32.name() : __M32,
        __M33.name() : __M33,
        __M34.name() : __M34,
        __M41.name() : __M41,
        __M42.name() : __M42,
        __M43.name() : __M43,
        __M44.name() : __M44,
        __CenterLocalX.name() : __CenterLocalX,
        __CenterLocalY.name() : __CenterLocalY
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_8 = CTD_ANON_8


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_9 (pyxb.binding.basis.complexTypeDefinition):
    """Description of a subpart of an image. It describes the location of the file and what detector it was acquired with."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 146, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element FileName uses Python identifier FileName
    __FileName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'FileName'), 'FileName', '__AbsentNamespace0_CTD_ANON_9_FileName', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 148, 4), )

    
    FileName = property(__FileName.value, __FileName.set, None, None)

    
    # Element DetectorName uses Python identifier DetectorName
    __DetectorName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'DetectorName'), 'DetectorName', '__AbsentNamespace0_CTD_ANON_9_DetectorName', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 149, 4), )

    
    DetectorName = property(__DetectorName.value, __DetectorName.set, None, None)

    _ElementMap.update({
        __FileName.name() : __FileName,
        __DetectorName.name() : __DetectorName
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_9 = CTD_ANON_9


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_10 (pyxb.binding.basis.complexTypeDefinition):
    """Representation of a shape supported by Atlas 5. It contains vertices that decribe the shape. Note: Rectangle and Oval are described with X and Y Size. While Polygons are described with Vertex Positions"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 157, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element Type uses Python identifier Type
    __Type = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Type'), 'Type', '__AbsentNamespace0_CTD_ANON_10_Type', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 159, 4), )

    
    Type = property(__Type.value, __Type.set, None, None)

    
    # Element Size uses Python identifier Size
    __Size = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Size'), 'Size', '__AbsentNamespace0_CTD_ANON_10_Size', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 169, 4), )

    
    Size = property(__Size.value, __Size.set, None, None)

    
    # Element Center uses Python identifier Center
    __Center = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Center'), 'Center', '__AbsentNamespace0_CTD_ANON_10_Center', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 181, 1), )

    
    Center = property(__Center.value, __Center.set, None, 'The rotation point of a geometry. Usually 0, 0. Note: a Polygon has no center per se. Its vertex positions determine its center')

    
    # Element Vertex uses Python identifier Vertex
    __Vertex = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Vertex'), 'Vertex', '__AbsentNamespace0_CTD_ANON_10_Vertex', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 192, 1), )

    
    Vertex = property(__Vertex.value, __Vertex.set, None, 'A Point in a polygon geometry')

    _ElementMap.update({
        __Type.name() : __Type,
        __Size.name() : __Size,
        __Center.name() : __Center,
        __Vertex.name() : __Vertex
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_10 = CTD_ANON_10


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_11 (pyxb.binding.basis.complexTypeDefinition):
    """Complex type [anonymous] with content type ELEMENT_ONLY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 170, 5)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element X uses Python identifier X
    __X = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'X'), 'X', '__AbsentNamespace0_CTD_ANON_11_X', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 172, 7), )

    
    X = property(__X.value, __X.set, None, None)

    
    # Element Y uses Python identifier Y
    __Y = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Y'), 'Y', '__AbsentNamespace0_CTD_ANON_11_Y', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 173, 7), )

    
    Y = property(__Y.value, __Y.set, None, None)

    _ElementMap.update({
        __X.name() : __X,
        __Y.name() : __Y
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_11 = CTD_ANON_11


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_12 (pyxb.binding.basis.complexTypeDefinition):
    """The rotation point of a geometry. Usually 0, 0. Note: a Polygon has no center per se. Its vertex positions determine its center"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 185, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element X uses Python identifier X
    __X = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'X'), 'X', '__AbsentNamespace0_CTD_ANON_12_X', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 187, 4), )

    
    X = property(__X.value, __X.set, None, None)

    
    # Element Y uses Python identifier Y
    __Y = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Y'), 'Y', '__AbsentNamespace0_CTD_ANON_12_Y', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 188, 4), )

    
    Y = property(__Y.value, __Y.set, None, None)

    _ElementMap.update({
        __X.name() : __X,
        __Y.name() : __Y
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_12 = CTD_ANON_12


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_13 (pyxb.binding.basis.complexTypeDefinition):
    """A Point in a polygon geometry"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 196, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element X uses Python identifier X
    __X = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'X'), 'X', '__AbsentNamespace0_CTD_ANON_13_X', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 198, 4), )

    
    X = property(__X.value, __X.set, None, None)

    
    # Element Y uses Python identifier Y
    __Y = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Y'), 'Y', '__AbsentNamespace0_CTD_ANON_13_Y', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 199, 4), )

    
    Y = property(__Y.value, __Y.set, None, None)

    _ElementMap.update({
        __X.name() : __X,
        __Y.name() : __Y
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_13 = CTD_ANON_13


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_14 (pyxb.binding.basis.complexTypeDefinition):
    """The spec for an ImportMosaic node is identical to the DataSet node, but it can only contain Images.  The ImportMosaic will be outlined and selectable in Atlas5 at the mosaic level - the individual images will not be individually selectable, alignable, etc."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 207, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element PlaceableImage uses Python identifier PlaceableImage
    __PlaceableImage = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'PlaceableImage'), 'PlaceableImage', '__AbsentNamespace0_CTD_ANON_14_PlaceableImage', True, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 46, 1), )

    
    PlaceableImage = property(__PlaceableImage.value, __PlaceableImage.set, None, 'Representation of Image on disk. Which could be actually Two files for two channels.  Images that are imported at thr root level or in Datasets will be individually outlined and selectable in the Atlas project.')

    
    # Element ParentTransform uses Python identifier ParentTransform
    __ParentTransform = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), 'ParentTransform', '__AbsentNamespace0_CTD_ANON_14_ParentTransform', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1), )

    
    ParentTransform = property(__ParentTransform.value, __ParentTransform.set, None, 'A 4X4 Matrix that represent the position, scale and shear of a placeable.')

    
    # Element Name uses Python identifier Name
    __Name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Name'), 'Name', '__AbsentNamespace0_CTD_ANON_14_Name', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 209, 4), )

    
    Name = property(__Name.value, __Name.set, None, None)

    _ElementMap.update({
        __PlaceableImage.name() : __PlaceableImage,
        __ParentTransform.name() : __ParentTransform,
        __Name.name() : __Name
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_14 = CTD_ANON_14


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_15 (pyxb.binding.basis.complexTypeDefinition):
    """For precision sites, an overview, single image is taken, some service provides a correction shift, and a single image high res image is taken using beam shift.  Precision sites are not imported by the regular import process, the Precision Site Automation tool must be used.  The parent transform should just be the position and rotation of the site."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 219, 2)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element ParentTransform uses Python identifier ParentTransform
    __ParentTransform = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), 'ParentTransform', '__AbsentNamespace0_CTD_ANON_15_ParentTransform', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1), )

    
    ParentTransform = property(__ParentTransform.value, __ParentTransform.set, None, 'A 4X4 Matrix that represent the position, scale and shear of a placeable.')

    
    # Element Name uses Python identifier Name
    __Name = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Name'), 'Name', '__AbsentNamespace0_CTD_ANON_15_Name', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 221, 4), )

    
    Name = property(__Name.value, __Name.set, None, 'The identifying name for the site.  This will be the file name for the saved high res image')

    
    # Element SaveLocation uses Python identifier SaveLocation
    __SaveLocation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'SaveLocation'), 'SaveLocation', '__AbsentNamespace0_CTD_ANON_15_SaveLocation', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 226, 4), )

    
    SaveLocation = property(__SaveLocation.value, __SaveLocation.set, None, 'The save location for the high res image.  Details to be discussed.  Probably the full path to the save location.')

    
    # Element Overview uses Python identifier Overview
    __Overview = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Overview'), 'Overview', '__AbsentNamespace0_CTD_ANON_15_Overview', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 232, 4), )

    
    Overview = property(__Overview.value, __Overview.set, None, 'Details for the overview image.  As a first cut, the geometry should be a rectangle with a center of (0,0) and the desired width and hieght of the overview image.  The software will take an image of the w and h up to the max tile size in the protocol.')

    
    # Element HighRes uses Python identifier HighRes
    __HighRes = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'HighRes'), 'HighRes', '__AbsentNamespace0_CTD_ANON_15_HighRes', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 251, 4), )

    
    HighRes = property(__HighRes.value, __HighRes.set, None, 'Details for the high res image.')

    _ElementMap.update({
        __ParentTransform.name() : __ParentTransform,
        __Name.name() : __Name,
        __SaveLocation.name() : __SaveLocation,
        __Overview.name() : __Overview,
        __HighRes.name() : __HighRes
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_15 = CTD_ANON_15


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_16 (pyxb.binding.basis.complexTypeDefinition):
    """Details for the overview image.  As a first cut, the geometry should be a rectangle with a center of (0,0) and the desired width and hieght of the overview image.  The software will take an image of the w and h up to the max tile size in the protocol."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 236, 5)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element Geometry uses Python identifier Geometry
    __Geometry = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Geometry'), 'Geometry', '__AbsentNamespace0_CTD_ANON_16_Geometry', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 153, 1), )

    
    Geometry = property(__Geometry.value, __Geometry.set, None, 'Representation of a shape supported by Atlas 5. It contains vertices that decribe the shape. Note: Rectangle and Oval are described with X and Y Size. While Polygons are described with Vertex Positions')

    
    # Element ProtocolName uses Python identifier ProtocolName
    __ProtocolName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'ProtocolName'), 'ProtocolName', '__AbsentNamespace0_CTD_ANON_16_ProtocolName', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 238, 7), )

    
    ProtocolName = property(__ProtocolName.value, __ProtocolName.set, None, 'The name of the Atlas protocol to use for the overview image.')

    _ElementMap.update({
        __Geometry.name() : __Geometry,
        __ProtocolName.name() : __ProtocolName
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_16 = CTD_ANON_16


# Complex type [anonymous] with content type ELEMENT_ONLY
class CTD_ANON_17 (pyxb.binding.basis.complexTypeDefinition):
    """Details for the high res image."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 255, 5)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element Geometry uses Python identifier Geometry
    __Geometry = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(Namespace, 'Geometry'), 'Geometry', '__AbsentNamespace0_CTD_ANON_17_Geometry', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 153, 1), )

    
    Geometry = property(__Geometry.value, __Geometry.set, None, 'Representation of a shape supported by Atlas 5. It contains vertices that decribe the shape. Note: Rectangle and Oval are described with X and Y Size. While Polygons are described with Vertex Positions')

    
    # Element ProtocolName uses Python identifier ProtocolName
    __ProtocolName = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'ProtocolName'), 'ProtocolName', '__AbsentNamespace0_CTD_ANON_17_ProtocolName', False, pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 257, 7), )

    
    ProtocolName = property(__ProtocolName.value, __ProtocolName.set, None, 'The name of the Atlas protocol to use for the hig res image.')

    _ElementMap.update({
        __Geometry.name() : __Geometry,
        __ProtocolName.name() : __ProtocolName
    })
    _AttributeMap.update({
        
    })
_module_typeBindings.CTD_ANON_17 = CTD_ANON_17


FibicsAtlas5Import = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'FibicsAtlas5Import'), CTD_ANON, documentation='All items to be imported are contained in this node.  acquired data (datasets, images and mosaics) will be placed in the imported date section of the project exaclty as they are structured in this file.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 4, 1))
Namespace.addCategoryObject('elementBinding', FibicsAtlas5Import.name().localName(), FibicsAtlas5Import)

DataSet = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'DataSet'), CTD_ANON_, documentation='Collection of data that has been aquired and is to be imported.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 32, 1))
Namespace.addCategoryObject('elementBinding', DataSet.name().localName(), DataSet)

PlaceableImage = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'PlaceableImage'), CTD_ANON_2, documentation='Representation of Image on disk. Which could be actually Two files for two channels.  Images that are imported at thr root level or in Datasets will be individually outlined and selectable in the Atlas project.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 46, 1))
Namespace.addCategoryObject('elementBinding', PlaceableImage.name().localName(), PlaceableImage)

SectionSet = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'SectionSet'), CTD_ANON_4, documentation='A collection of Sections that define a group of regions', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 65, 1))
Namespace.addCategoryObject('elementBinding', SectionSet.name().localName(), SectionSet)

RegionSet = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'RegionSet'), CTD_ANON_5, documentation='A colection of Atlas Regions', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 77, 1))
Namespace.addCategoryObject('elementBinding', RegionSet.name().localName(), RegionSet)

AtlasRegion = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'AtlasRegion'), CTD_ANON_6, documentation='A geo that describes an area of interest', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 89, 1))
Namespace.addCategoryObject('elementBinding', AtlasRegion.name().localName(), AtlasRegion)

Section = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Section'), CTD_ANON_7, documentation='Special Atlas Region that leaves in a SectionSet as geo representations of individual regions', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 102, 1))
Namespace.addCategoryObject('elementBinding', Section.name().localName(), Section)

ParentTransform = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), CTD_ANON_8, documentation='A 4X4 Matrix that represent the position, scale and shear of a placeable.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1))
Namespace.addCategoryObject('elementBinding', ParentTransform.name().localName(), ParentTransform)

Channel = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Channel'), CTD_ANON_9, documentation='Description of a subpart of an image. It describes the location of the file and what detector it was acquired with.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 142, 1))
Namespace.addCategoryObject('elementBinding', Channel.name().localName(), Channel)

Geometry = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Geometry'), CTD_ANON_10, documentation='Representation of a shape supported by Atlas 5. It contains vertices that decribe the shape. Note: Rectangle and Oval are described with X and Y Size. While Polygons are described with Vertex Positions', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 153, 1))
Namespace.addCategoryObject('elementBinding', Geometry.name().localName(), Geometry)

Center = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Center'), CTD_ANON_12, documentation='The rotation point of a geometry. Usually 0, 0. Note: a Polygon has no center per se. Its vertex positions determine its center', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 181, 1))
Namespace.addCategoryObject('elementBinding', Center.name().localName(), Center)

Vertex = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Vertex'), CTD_ANON_13, documentation='A Point in a polygon geometry', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 192, 1))
Namespace.addCategoryObject('elementBinding', Vertex.name().localName(), Vertex)

ImportMosaic = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ImportMosaic'), CTD_ANON_14, documentation='The spec for an ImportMosaic node is identical to the DataSet node, but it can only contain Images.  The ImportMosaic will be outlined and selectable in Atlas5 at the mosaic level - the individual images will not be individually selectable, alignable, etc.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 203, 1))
Namespace.addCategoryObject('elementBinding', ImportMosaic.name().localName(), ImportMosaic)

PrecisionSiteSpec = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'PrecisionSiteSpec'), CTD_ANON_15, documentation='For precision sites, an overview, single image is taken, some service provides a correction shift, and a single image high res image is taken using beam shift.  Precision sites are not imported by the regular import process, the Precision Site Automation tool must be used.  The parent transform should just be the position and rotation of the site.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 215, 1))
Namespace.addCategoryObject('elementBinding', PrecisionSiteSpec.name().localName(), PrecisionSiteSpec)



CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'DataSet'), CTD_ANON_, scope=CTD_ANON, documentation='Collection of data that has been aquired and is to be imported.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 32, 1)))

CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'PlaceableImage'), CTD_ANON_2, scope=CTD_ANON, documentation='Representation of Image on disk. Which could be actually Two files for two channels.  Images that are imported at thr root level or in Datasets will be individually outlined and selectable in the Atlas project.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 46, 1)))

CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'SectionSet'), CTD_ANON_4, scope=CTD_ANON, documentation='A collection of Sections that define a group of regions', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 65, 1)))

CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'AtlasRegion'), CTD_ANON_6, scope=CTD_ANON, documentation='A geo that describes an area of interest', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 89, 1)))

CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ImportMosaic'), CTD_ANON_14, scope=CTD_ANON, documentation='The spec for an ImportMosaic node is identical to the DataSet node, but it can only contain Images.  The ImportMosaic will be outlined and selectable in Atlas5 at the mosaic level - the individual images will not be individually selectable, alignable, etc.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 203, 1)))

CTD_ANON._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'PrecisionSiteSpec'), CTD_ANON_15, scope=CTD_ANON, documentation='For precision sites, an overview, single image is taken, some service provides a correction shift, and a single image high res image is taken using beam shift.  Precision sites are not imported by the regular import process, the Precision Site Automation tool must be used.  The parent transform should just be the position and rotation of the site.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 215, 1)))

def _BuildAutomaton ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton
    del _BuildAutomaton
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 10, 4))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 11, 4))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 12, 4))
    counters.add(cc_2)
    cc_3 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 13, 4))
    counters.add(cc_3)
    cc_4 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 18, 4))
    counters.add(cc_4)
    cc_5 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 23, 4))
    counters.add(cc_5)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'DataSet')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 10, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AtlasRegion')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 11, 4))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'SectionSet')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 12, 4))
    st_2 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_3, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'PlaceableImage')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 13, 4))
    st_3 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_4, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImportMosaic')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 18, 4))
    st_4 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_5, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'PrecisionSiteSpec')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 23, 4))
    st_5 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_2, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_2, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_3, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_3, False) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_3, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_4, True) ]))
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_4, False) ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
        fac.UpdateInstruction(cc_5, True) ]))
    st_5._set_transitionSet(transitions)
    return fac.Automaton(states, counters, True, containing_state=None)
CTD_ANON._Automaton = _BuildAutomaton()




CTD_ANON_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'DataSet'), CTD_ANON_, scope=CTD_ANON_, documentation='Collection of data that has been aquired and is to be imported.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 32, 1)))

CTD_ANON_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Name'), pyxb.binding.datatypes.anyType, scope=CTD_ANON_, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 38, 4)))

CTD_ANON_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'PlaceableImage'), CTD_ANON_2, scope=CTD_ANON_, documentation='Representation of Image on disk. Which could be actually Two files for two channels.  Images that are imported at thr root level or in Datasets will be individually outlined and selectable in the Atlas project.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 46, 1)))

CTD_ANON_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), CTD_ANON_8, scope=CTD_ANON_, documentation='A 4X4 Matrix that represent the position, scale and shear of a placeable.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1)))

CTD_ANON_._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ImportMosaic'), CTD_ANON_14, scope=CTD_ANON_, documentation='The spec for an ImportMosaic node is identical to the DataSet node, but it can only contain Images.  The ImportMosaic will be outlined and selectable in Atlas5 at the mosaic level - the individual images will not be individually selectable, alignable, etc.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 203, 1)))

def _BuildAutomaton_ ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_
    del _BuildAutomaton_
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 40, 4))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 41, 4))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 42, 4))
    counters.add(cc_2)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(None, 'Name')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 38, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 39, 4))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'PlaceableImage')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 40, 4))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'DataSet')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 41, 4))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ImportMosaic')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 42, 4))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    transitions.append(fac.Transition(st_4, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_4._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_._Automaton = _BuildAutomaton_()




CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Name'), pyxb.binding.datatypes.string, scope=CTD_ANON_2, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 52, 4)))

CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'FileName'), pyxb.binding.datatypes.string, scope=CTD_ANON_2, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 54, 4)))

CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Channels'), CTD_ANON_3, scope=CTD_ANON_2, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 55, 4)))

CTD_ANON_2._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), CTD_ANON_8, scope=CTD_ANON_2, documentation='A 4X4 Matrix that represent the position, scale and shear of a placeable.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1)))

def _BuildAutomaton_2 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_2
    del _BuildAutomaton_2
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(None, 'Name')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 52, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 53, 4))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(None, 'FileName')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 54, 4))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(None, 'Channels')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 55, 4))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_2._Automaton = _BuildAutomaton_2()




CTD_ANON_3._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Channel'), CTD_ANON_9, scope=CTD_ANON_3, documentation='Description of a subpart of an image. It describes the location of the file and what detector it was acquired with.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 142, 1)))

def _BuildAutomaton_3 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_3
    del _BuildAutomaton_3
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=1, max=2, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 58, 7))
    counters.add(cc_0)
    states = []
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_3._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Channel')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 58, 7))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_0._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_3._Automaton = _BuildAutomaton_3()




CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Name'), pyxb.binding.datatypes.string, scope=CTD_ANON_4, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 71, 4)))

CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Section'), CTD_ANON_7, scope=CTD_ANON_4, documentation='Special Atlas Region that leaves in a SectionSet as geo representations of individual regions', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 102, 1)))

CTD_ANON_4._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), CTD_ANON_8, scope=CTD_ANON_4, documentation='A 4X4 Matrix that represent the position, scale and shear of a placeable.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1)))

def _BuildAutomaton_4 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_4
    del _BuildAutomaton_4
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(None, 'Name')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 71, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 72, 4))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_4._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Section')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 73, 4))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_4._Automaton = _BuildAutomaton_4()




CTD_ANON_5._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Name'), pyxb.binding.datatypes.string, scope=CTD_ANON_5, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 83, 4)))

CTD_ANON_5._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'AtlasRegion'), CTD_ANON_6, scope=CTD_ANON_5, documentation='A geo that describes an area of interest', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 89, 1)))

CTD_ANON_5._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), CTD_ANON_8, scope=CTD_ANON_5, documentation='A 4X4 Matrix that represent the position, scale and shear of a placeable.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1)))

def _BuildAutomaton_5 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_5
    del _BuildAutomaton_5
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 83, 4))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(None, 'Name')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 83, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 84, 4))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_5._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'AtlasRegion')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 85, 4))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_5._Automaton = _BuildAutomaton_5()




CTD_ANON_6._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Name'), pyxb.binding.datatypes.anyType, scope=CTD_ANON_6, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 95, 4)))

CTD_ANON_6._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'RotationCenter'), pyxb.binding.datatypes.double, scope=CTD_ANON_6, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 98, 4)))

CTD_ANON_6._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), CTD_ANON_8, scope=CTD_ANON_6, documentation='A 4X4 Matrix that represent the position, scale and shear of a placeable.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1)))

CTD_ANON_6._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Geometry'), CTD_ANON_10, scope=CTD_ANON_6, documentation='Representation of a shape supported by Atlas 5. It contains vertices that decribe the shape. Note: Rectangle and Oval are described with X and Y Size. While Polygons are described with Vertex Positions', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 153, 1)))

def _BuildAutomaton_6 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_6
    del _BuildAutomaton_6
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 98, 4))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_6._UseForTag(pyxb.namespace.ExpandedName(None, 'Name')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 95, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_6._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 96, 4))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_6._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Geometry')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 97, 4))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_6._UseForTag(pyxb.namespace.ExpandedName(None, 'RotationCenter')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 98, 4))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_6._Automaton = _BuildAutomaton_6()




CTD_ANON_7._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Name'), pyxb.binding.datatypes.anyType, scope=CTD_ANON_7, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 108, 4)))

CTD_ANON_7._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'RotationCenter'), pyxb.binding.datatypes.double, scope=CTD_ANON_7, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 111, 4), unicode_default='0'))

CTD_ANON_7._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), CTD_ANON_8, scope=CTD_ANON_7, documentation='A 4X4 Matrix that represent the position, scale and shear of a placeable.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1)))

CTD_ANON_7._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Geometry'), CTD_ANON_10, scope=CTD_ANON_7, documentation='Representation of a shape supported by Atlas 5. It contains vertices that decribe the shape. Note: Rectangle and Oval are described with X and Y Size. While Polygons are described with Vertex Positions', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 153, 1)))

def _BuildAutomaton_7 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_7
    del _BuildAutomaton_7
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 111, 4))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_7._UseForTag(pyxb.namespace.ExpandedName(None, 'Name')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 108, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_7._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 109, 4))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_7._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Geometry')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 110, 4))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_7._UseForTag(pyxb.namespace.ExpandedName(None, 'RotationCenter')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 111, 4))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_7._Automaton = _BuildAutomaton_7()




CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M11'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 121, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M12'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 122, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M13'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 123, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M14'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 124, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M21'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 125, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M22'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 126, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M23'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 127, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M24'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 128, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M31'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 129, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M32'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 130, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M33'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 131, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M34'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 132, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M41'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 133, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M42'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 134, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M43'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 135, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'M44'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 136, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'CenterLocalX'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 137, 4)))

CTD_ANON_8._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'CenterLocalY'), pyxb.binding.datatypes.double, scope=CTD_ANON_8, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 138, 4)))

def _BuildAutomaton_8 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_8
    del _BuildAutomaton_8
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M11')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 121, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M12')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 122, 4))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M13')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 123, 4))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M14')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 124, 4))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M21')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 125, 4))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M22')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 126, 4))
    st_5 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_5)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M23')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 127, 4))
    st_6 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_6)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M24')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 128, 4))
    st_7 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_7)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M31')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 129, 4))
    st_8 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_8)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M32')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 130, 4))
    st_9 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_9)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M33')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 131, 4))
    st_10 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_10)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M34')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 132, 4))
    st_11 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_11)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M41')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 133, 4))
    st_12 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_12)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M42')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 134, 4))
    st_13 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_13)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M43')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 135, 4))
    st_14 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_14)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'M44')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 136, 4))
    st_15 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_15)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'CenterLocalX')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 137, 4))
    st_16 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_16)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_8._UseForTag(pyxb.namespace.ExpandedName(None, 'CenterLocalY')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 138, 4))
    st_17 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_17)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_5, [
         ]))
    st_4._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_6, [
         ]))
    st_5._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_7, [
         ]))
    st_6._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_8, [
         ]))
    st_7._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_9, [
         ]))
    st_8._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_10, [
         ]))
    st_9._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_11, [
         ]))
    st_10._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_12, [
         ]))
    st_11._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_13, [
         ]))
    st_12._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_14, [
         ]))
    st_13._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_15, [
         ]))
    st_14._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_16, [
         ]))
    st_15._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_17, [
         ]))
    st_16._set_transitionSet(transitions)
    transitions = []
    st_17._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_8._Automaton = _BuildAutomaton_8()




CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'FileName'), pyxb.binding.datatypes.string, scope=CTD_ANON_9, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 148, 4)))

CTD_ANON_9._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'DetectorName'), pyxb.binding.datatypes.string, scope=CTD_ANON_9, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 149, 4)))

def _BuildAutomaton_9 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_9
    del _BuildAutomaton_9
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(None, 'FileName')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 148, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_9._UseForTag(pyxb.namespace.ExpandedName(None, 'DetectorName')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 149, 4))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_9._Automaton = _BuildAutomaton_9()




CTD_ANON_10._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Type'), STD_ANON, scope=CTD_ANON_10, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 159, 4), unicode_default='Rectangle'))

CTD_ANON_10._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Size'), CTD_ANON_11, scope=CTD_ANON_10, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 169, 4)))

CTD_ANON_10._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Center'), CTD_ANON_12, scope=CTD_ANON_10, documentation='The rotation point of a geometry. Usually 0, 0. Note: a Polygon has no center per se. Its vertex positions determine its center', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 181, 1)))

CTD_ANON_10._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Vertex'), CTD_ANON_13, scope=CTD_ANON_10, documentation='A Point in a polygon geometry', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 192, 1)))

def _BuildAutomaton_10 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_10
    del _BuildAutomaton_10
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 168, 4))
    counters.add(cc_0)
    cc_1 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 169, 4))
    counters.add(cc_1)
    cc_2 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 177, 4))
    counters.add(cc_2)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(None, 'Type')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 159, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Center')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 168, 4))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_1, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(None, 'Size')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 169, 4))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_2, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_10._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Vertex')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 177, 4))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    transitions.append(fac.Transition(st_2, [
         ]))
    transitions.append(fac.Transition(st_3, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_0, False) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
        fac.UpdateInstruction(cc_1, True) ]))
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_1, False) ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
        fac.UpdateInstruction(cc_2, True) ]))
    st_3._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_10._Automaton = _BuildAutomaton_10()




CTD_ANON_11._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'X'), pyxb.binding.datatypes.double, scope=CTD_ANON_11, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 172, 7)))

CTD_ANON_11._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Y'), pyxb.binding.datatypes.double, scope=CTD_ANON_11, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 173, 7)))

def _BuildAutomaton_11 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_11
    del _BuildAutomaton_11
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_11._UseForTag(pyxb.namespace.ExpandedName(None, 'X')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 172, 7))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_11._UseForTag(pyxb.namespace.ExpandedName(None, 'Y')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 173, 7))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_11._Automaton = _BuildAutomaton_11()




CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'X'), pyxb.binding.datatypes.double, scope=CTD_ANON_12, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 187, 4)))

CTD_ANON_12._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Y'), pyxb.binding.datatypes.double, scope=CTD_ANON_12, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 188, 4)))

def _BuildAutomaton_12 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_12
    del _BuildAutomaton_12
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(None, 'X')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 187, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_12._UseForTag(pyxb.namespace.ExpandedName(None, 'Y')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 188, 4))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_12._Automaton = _BuildAutomaton_12()




CTD_ANON_13._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'X'), pyxb.binding.datatypes.anyType, scope=CTD_ANON_13, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 198, 4)))

CTD_ANON_13._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Y'), pyxb.binding.datatypes.anyType, scope=CTD_ANON_13, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 199, 4)))

def _BuildAutomaton_13 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_13
    del _BuildAutomaton_13
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_13._UseForTag(pyxb.namespace.ExpandedName(None, 'X')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 198, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_13._UseForTag(pyxb.namespace.ExpandedName(None, 'Y')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 199, 4))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_13._Automaton = _BuildAutomaton_13()




CTD_ANON_14._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'PlaceableImage'), CTD_ANON_2, scope=CTD_ANON_14, documentation='Representation of Image on disk. Which could be actually Two files for two channels.  Images that are imported at thr root level or in Datasets will be individually outlined and selectable in the Atlas project.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 46, 1)))

CTD_ANON_14._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), CTD_ANON_8, scope=CTD_ANON_14, documentation='A 4X4 Matrix that represent the position, scale and shear of a placeable.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1)))

CTD_ANON_14._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Name'), pyxb.binding.datatypes.string, scope=CTD_ANON_14, location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 209, 4)))

def _BuildAutomaton_14 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_14
    del _BuildAutomaton_14
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(None, 'Name')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 209, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 210, 4))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_14._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'PlaceableImage')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 211, 4))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_2._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_14._Automaton = _BuildAutomaton_14()




CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform'), CTD_ANON_8, scope=CTD_ANON_15, documentation='A 4X4 Matrix that represent the position, scale and shear of a placeable.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 115, 1)))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Name'), pyxb.binding.datatypes.string, scope=CTD_ANON_15, documentation='The identifying name for the site.  This will be the file name for the saved high res image', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 221, 4)))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'SaveLocation'), pyxb.binding.datatypes.string, scope=CTD_ANON_15, documentation='The save location for the high res image.  Details to be discussed.  Probably the full path to the save location.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 226, 4)))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Overview'), CTD_ANON_16, scope=CTD_ANON_15, documentation='Details for the overview image.  As a first cut, the geometry should be a rectangle with a center of (0,0) and the desired width and hieght of the overview image.  The software will take an image of the w and h up to the max tile size in the protocol.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 232, 4)))

CTD_ANON_15._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'HighRes'), CTD_ANON_17, scope=CTD_ANON_15, documentation='Details for the high res image.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 251, 4)))

def _BuildAutomaton_15 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_15
    del _BuildAutomaton_15
    import pyxb.utils.fac as fac

    counters = set()
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(None, 'Name')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 221, 4))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(None, 'SaveLocation')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 226, 4))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'ParentTransform')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 231, 4))
    st_2 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_2)
    final_update = None
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(None, 'Overview')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 232, 4))
    st_3 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_3)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_15._UseForTag(pyxb.namespace.ExpandedName(None, 'HighRes')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 251, 4))
    st_4 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_4)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_2, [
         ]))
    st_1._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_3, [
         ]))
    st_2._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_4, [
         ]))
    st_3._set_transitionSet(transitions)
    transitions = []
    st_4._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_15._Automaton = _BuildAutomaton_15()




CTD_ANON_16._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Geometry'), CTD_ANON_10, scope=CTD_ANON_16, documentation='Representation of a shape supported by Atlas 5. It contains vertices that decribe the shape. Note: Rectangle and Oval are described with X and Y Size. While Polygons are described with Vertex Positions', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 153, 1)))

CTD_ANON_16._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'ProtocolName'), pyxb.binding.datatypes.string, scope=CTD_ANON_16, documentation='The name of the Atlas protocol to use for the overview image.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 238, 7)))

def _BuildAutomaton_16 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_16
    del _BuildAutomaton_16
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 243, 7))
    counters.add(cc_0)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_16._UseForTag(pyxb.namespace.ExpandedName(None, 'ProtocolName')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 238, 7))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_16._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Geometry')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 243, 7))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_16._Automaton = _BuildAutomaton_16()




CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'Geometry'), CTD_ANON_10, scope=CTD_ANON_17, documentation='Representation of a shape supported by Atlas 5. It contains vertices that decribe the shape. Note: Rectangle and Oval are described with X and Y Size. While Polygons are described with Vertex Positions', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 153, 1)))

CTD_ANON_17._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'ProtocolName'), pyxb.binding.datatypes.string, scope=CTD_ANON_17, documentation='The name of the Atlas protocol to use for the hig res image.', location=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 257, 7)))

def _BuildAutomaton_17 ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_17
    del _BuildAutomaton_17
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=1, metadata=pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 262, 7))
    counters.add(cc_0)
    states = []
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(None, 'ProtocolName')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 257, 7))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    final_update.add(fac.UpdateInstruction(cc_0, False))
    symbol = pyxb.binding.content.ElementUse(CTD_ANON_17._UseForTag(pyxb.namespace.ExpandedName(Namespace, 'Geometry')), pyxb.utils.utility.Location('/nas/ATLASimport/FibicsAtlasImport_1_1.xsd', 262, 7))
    st_1 = fac.State(symbol, is_initial=False, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_1, [
         ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, True) ]))
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
CTD_ANON_17._Automaton = _BuildAutomaton_17()

