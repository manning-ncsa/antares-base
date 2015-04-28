from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

class Locus( models.Model ):
    """
    The class corresponds to the 'Locus' table.
    """
    LocusID = models.IntegerField( primary_key=True )
    RA = models.FloatField()
    Decl = models.FloatField()

class Alert( models.Model ):
    """
    The class corresponds to the 'Alert' table.
    """
    decisions = (
        ( 'NA', 'Not Applicable' ),
        ( 'T', 'Throttled Alert' ),
        ( 'D', 'Diverted' ),
        ( 'L1', 'Level-I Alert' ),
        ( 'L2', 'Level-II Alert' ),
        ( 'R', 'Rarest of the rare Alert' ),
    )

    AlertID = models.IntegerField( primary_key=True )
    LocusID = models.ForeignKey( Locus )
    Decision = models.CharField( max_length=50,
                                 choices=decisions,
                                 default='NA' )

class AlertReplica( models.Model ):
    """
    The class corresponds to the 'AlertReplica' table.
    """
    ReplicaID = models.IntegerField( primary_key=True )
    AlertID = models.ForeignKey( Alert )
    AstroObjectID = models.ForeignKey( AstroObject )
    # put a >0 constraint on ReplicaNumber field
    ReplicaNumber = models.IntegerField( validators=[MinValueValidator(1)] )
    LocusID = models.ForeignKey( Locus )
    ChannelID = models.IntegerField()
    ChannelProbability = models.FloatField()

class AstroObject( models.Model ):
    """
    The class corresponds to the 'AlertReplica' table.
    """
    AstroObjectID = models.IntegerField( primary_key=True )
    LocusID = models.ForeignKey( Locus )
    Catalog = models.CharField( max_length=500 )
    IDinCatalog = models.IntegerField()
    IsPointSource = models.BooleanField( default=False )

class Attribute( models.Model ):
    """
    The class corresponds to the 'Attribute' table.
    """
    AttrName = models.CharField( max_length=100, primary_key=True )
    IsScaled = models.BooleanField( default=False )
    DataType = models.CharField( max_length=500 )

class AttributeValue( models.Model ):
    """
    The class corresponds to the 'AttributeValue' table.
    """
    # List of choices of type a container can be
    container_types = (
        ( 'A', 'AstroObject Table' ),
        ( 'C', 'Combo Table' ),
        ( 'I', 'Image Table' ),
        ( 'E', 'Alert Table' ),
        ( 'L', 'LocusAggregatedAlert Table' ),
        ( 'M', 'ImageSection Table' ),
        ( 'R', 'AlertReplica Table' ),
        ( 'S', 'Source Table' ),
    )

    #AttributeValueID = models.IntegerField( primary_key=True )
    AttrName = models.ForeignKey( Attribute )
    ContainerID = models.IntegerField()
    ContainerType = models.CharField( max_length=1, choices=container_types )
    ComputedAt = models.DateTimeField( 'Time the value was computed' )
    # Seems that attributes used in the demo are all floats.
    Value = models.FloatField()
    Annotation = models.CharField( max_length=500 )
    Confidence = models.FloatField()

    class Meta:
        unique_together = ( 'AttrName', 'ContainerID',
                            'ContainerType', 'ComputedAt' )

