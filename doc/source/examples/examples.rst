***************************************
Examples of using API
***************************************

How to assign/retrieve the value to/from an attribute
=====================================================

Suppose we have a camera alert ``alert`` with some base attributes, for example,
its ``G`` value and ``R`` value, if want to compute the derived
attribute ``GMinusR`` which belongs to ``CA`` context, we can do::

  from antares.alert import CameraAlert

  def computeGMinusR( alert ):
      """'alert' is a camera alert """
      alert.CA.GMinusR = alert.CA.G - alert.CA.R
      alert.CA.GMinusR.confidence = 1.0
      alert.CA.GMinusR.annotation = "High confidence because we don't know"
      alert.CA.GMinusR.description = "G value minus R value"

If ``alert`` does not have ``CA`` context or 
attribute ``GMinusR`` is not valid under ``CA`` context,
:py:exc:`AttributeError` exception will be raised.
		
Diverting an alert
=====================================================

If we want to divert a camera alert ``alert`` based on the size of
attribute ``LightCurve`` under ``LA`` context, we can do::

  if len( alert.LA.Lightcurve ) > MAX_LIGHT_CURVE_SIZE:
      alert.divert( "Light curve is too big" )

Creating an alert replica
=========================

If we want to create a replica of a camera alert ``alert`` without
associating an astro object, we can do::

  alert.createReplica()

To associate an astro object ``astro`` when creating a replica, we
do::

  alert.createReplica( astroobj=astro )

Creating a combo based on the value of attribute ``RedShift``
=============================================================

We can create combos for a camera alert ``alert`` based on the value
of attribute ``RedShift`` which belongs to ``AR`` context::

  def CreateComboOnRedshift( alert ):
    """
    Create combos based on attribute redshift. 'alert' is a camera alert.
    """
    if alert.Type != CAMERA_ALERT:
        return

    ## combo forking
    replica_set1 = []
    replica_set2 = []
    for replica in alert.replicas:
        ## group replicas with lower redshift value together
        if replica.AR.RedShift < 0.5:
            replica_set1.append( replica )
        else:
            replica_set2.append( replica )

    if len(replica_set1) > 0:
        alert.CA.createCombo( replica_set1 )
    if len(replica_set2) > 0:
        alert.CA.createCombo( replica_set2 )

Different ways of iterating attribute values
============================================

Iterating values of alert replicas of a camera alert
----------------------------------------------------

>>> import numpy as np
>>> values = alert.CA.assembleVector( 'AR', 'Redshift' )
>>> for val in np.nditer( values ):
>>>     print( val )

Here, ``alert`` is a camera alert. The second line of code returns a
numpy array of all the values of attribute ``Redshift`` under ``AR``
context of replicas of ``alert``.