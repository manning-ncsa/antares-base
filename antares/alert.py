from antares.context import *
#from antares.helper import hashuuid
import threading
import uuid
import random

HASH_SIZE = 100

def hashuuid( s ):
    n = 0
    for c in str(s):
        n += ord( c )

    n = n - random.randint(1, 1000)
    return n % HASH_SIZE


class Alert( object ):
    """Represents a general alert. It is the super class of :py:class:`CameraAlert`
    and :py:class:`ExternalAlert` where a camera alert is generated by LSST and an
    external alert is from sources other than LSST."""

    def __init__( self, alert_id, ra, decl ):
        """Initialize with an Alert ID."""
        self.ID = alert_id
        self.ra = ra
        self.decl = decl

    def isPresent( self, context ):
        """
        Check if the context for the Alert is currently present.

        :param string context: name of the context. e.g. 'CA', 'AR', etc.

        :return: :py:data:`True` if the context is currently present,
                 otherwise :py:data:`False`.
        """
        if hasattr(self, context):
            return True
        else:
            return False


class ExternalAlert( Alert ):
    """Represents an external alert which is a sub-class of :py:class:`Alert`.
    An external alert is from sources other than LSST."""
    pass
    
class CameraAlert( Alert ):
    """
    Represents a camera alert which is a sub-class of :py:class:`Alert`.
    A camera alert is associated with CA, IM, IR, IS and LA context objects.
    and is initialized with these 5 available contexts.

    :param: :py:class:`antares.context.CAContext` CA: CA context object
    :param: :py:class:`antares.context.IMContext` IM: IM context object
    :param: :py:class:`antares.context.IRContext` IR: IR context object
    :param: :py:class:`antares.context.ISContext` IS: IS context object
    :param: :py:class:`antares.context.LAContext` LA: LA context object
    """
    
    CA = None
    """
    CA (Camera Alert) context object. CA attributes are always available.

    :type: :py:class:`antares.context.CAContext`
    """

    IM = None
    """IM (Image) context object.

    :type: :py:class:`antares.context.IMContext`
    """

    IR = None
    """IR (Image RAFT) context object.

    :type: :py:class:`antares.context.IRContext`
    """

    IS = None
    """IS (Image Section) context object.
    
    :type: :py:class:`antares.context.ISContext`
    """

    LA = None
    """LA (Locus-aggregated Alert) context object. LA attributes are always available.

    :type: :py:class:`antares.context.LAContext`
    """

    replicas = None
    """
    A list of the alert replicas created by camera alert.

    :type: list
    """

    annotation = ''
    """
    Annotation of the camera alert.

    :type: string
    """

    def __init__( self, alert_id, ra, decl, CA, decision, locus_id, IM=None, IR=None, IS=None ):
        super().__init__( alert_id, ra, decl )
        self.CA = CA
        self.LA = LAContext( alert_id ) # LA context is implicit
        # When a camera alert is constructed, its decision is always not applicable.
        self.decision = decision
        self.locus_id = locus_id
        self.replica_num = 1 # used to keep track of replica numbers. Start with 1.
        self.replicas = []
        self.replica_counter = 0

    def __str__( self ):
        return 'Alert {0} at (ra={1}, dec={2}) Decision={3}\n{4}'.format(
            self.ID, self.ra, self.decl, self.decision, self.CA)

    def hasReplicas( self ):
        """
        Check whether alert has replicas.

        :return: :py:data:`True` if alert has replicas, otherwise :py:data:`False`.
        """
        if len(self.replicas) == 0:
            return False
        else:
            return True

    def createReplica( self, astro_id=None ):
        """
        Create an alert replica which is associated with an
        optional astro object id ``astro_id``.

        :param: :py:class:`int` astro_id: ID of the astro object
                to be associated with the created replica. It is optional.
        """
        conn = pymysql.connect(host='localhost', user='root',
                               passwd='', db='antares_demo')
        cursor = conn.cursor()
        query = "select ReplicaID from AlertReplica where AlertID={0}".format(self.ID)
        cursor.execute(query)
        id_postfix = len(cursor.fetchall()) + 1
        
        #id_postfix = hashuuid( uuid.uuid4() )
        #print( 'id_postfix = ', id_postfix )
        replica_id = int( str(self.ID) + str(id_postfix) )

        #print( 'replica count = ', self.replica_count )
        replica = AlertReplica( self, astro_id=astro_id, init_from_db=False,
                                replica_id=replica_id, replica_num=id_postfix )
        
        ## Update status for the newly created replica.

        ## TODO: call Zhe's system API.

        # conn = pymysql.connect(host='localhost', user='root',
        #                        passwd='', db='antares_demo')
        # cursor = conn.cursor()
        # query = "INSERT INTO AlertStatus VALUES \
        # ({}, 'a', 'w', 0, {}, {})".format(replica.ID, self.ID, self.ID)
        # cursor.execute(query)
        # conn.commit()
        # conn.close()

        replica.commit()
        replica.flushed2DB = True
        self.replicas.append( replica )
        return replica.ID

    def createCombo( self, replicas ):
        """
        Create an alert combo object which contains a set of
        alert replicas.

        :param list replicas: a list of alert replicas
        """
        pass

    def throttle( self, annotation ):
        """
        Throttle the alert.
        
        :param string annotation: a short description of why the alert is throttled.
        """
        pass

    def divert( self, annotation ):
        """
        Divert the alert.

        :param string annotation: a short description of why the alert is diverted.
        """
        self.decision = 'D'

        ## TODO: reflect the change of decision immediately to DB.
        conn = pymysql.connect(host='localhost', user='root',
                               passwd='', db='antares_demo')
        cursor = conn.cursor()
        sql_update = """update Alert set Decision="{0}", Annotation="{1}" where AlertID={2}""".format(
            self.decision, annotation, self.ID )
        cursor.execute( sql_update )
        conn.commit()
        conn.close()
        
        ## TODO: call Zhe's system API.
        
        #conn = pymysql.connect(host='localhost', user='root',
        #                       passwd='', db='antares_demo')
        # cursor = conn.cursor()
        # query = "INSERT INTO AlertStatus VALUES \
        # ({}, 'a', 'f', 0, {}, {})".format(self.ID, self.ID, self.ID)
        # cursor.execute(query)
        # conn.commit()
        # conn.close()

    def mark_as_rare( self, annotation ):
        """
        Mark the alert as a rare alert.

        :param string annotation: a short description of why the alert is rare.
        """
        conn = pymysql.connect(host='localhost', user='root',
                               passwd='', db='antares_demo')
        cursor = conn.cursor()

        if self.decision == 'R':
            sql_query = """select Annotation from Alert where AlertID={0}""".format(self.ID)
            cursor.execute( sql_query )
            self._annotation = cursor.fetchall()[0][0]
            self._annotation += '; ' + annotation
        else:
            self._annotation = annotation
            self.decision = 'R'

        ## TODO: reflect the change of decision immediately to DB.
        sql_update = """update Alert set Decision="{0}", Annotation="{1}" where AlertID={2}""".format(
            self.decision, self._annotation, self.ID )
        cursor.execute( sql_update )
        conn.commit()
        conn.close()
        
        ## TODO: call Zhe's system API.

    @property
    def annotation( self ):
        conn = pymysql.connect(host='localhost', user='root',
                               passwd='', db='antares_demo')
        cursor = conn.cursor()

        sql_query = """select Annotation from Alert where AlertID={0}""".format(self.ID)
        cursor.execute( sql_query )
        return cursor.fetchall()[0][0]

    def commit( self ):
        """
        Commit the alert data to Locus-aggregated Alerts DB.
        """
        conn = pymysql.connect( host='127.0.0.1', user='root',
                                passwd='', db='antares_demo' )
        cur = conn.cursor()

        # Nothing to commit for CA context now since all attributes are pre-loaded to DB.
        # self.CA.commit( cur )
        
        if self.decision != 'NA':
            ## Update corresponding Alert table to reflect decision change.
            ## Connect to mysql database.            
            sql_update = """update Alert set Decision="{0}" where AlertID={1}""".format(
                self.decision, self.ID )
            cur.execute( sql_update )

        # Replicas will be written to DB when they are created.
        # for replica in self.replicas:
        #    replica.commit()

        conn.commit()
        conn.close()

class AlertReplica( CameraAlert ):
    """
    Represents an alert replica. It is a sub-class of :py:class:`CameraAlert`.
    Beyond contexts available for CameraAlert, an alert replica is also
    associated with AO, AR, ES, LA, and PS context objects.
    Replica is initialized with its associated astro object (optional).

    :param: parent(:py:class:`antares.alert.CameraAlert`): parent of the alert replica.
    :param: astr_id(int): ID of the associated astro object (optional). 
    :param: init_from_db(boolean): indicate if the replica is initialized from Database (optional).
    :param: replica_id(int): ID of the alert replica (unique among all replicas).
    :param: replica_num(int): Number of the alert replica (unique among all replicas that share the same parent).
    """
    
    AR = None
    """
    AR (Alert Replica) context object.
    AR attributes are only accessible during per-replica processing.

    :type: :py:class:`antares.context.ARContext`
    """

    AO = None
    """AO (Astro Object) context object. AO attributes are available if
    ``AR.HasAstroObject`` = :py:data:`True`.

    :type: :py:class:`antares.context.AOContext`
    """

    ES = None
    """ES (Extended Source) context object. ES attributes are available only
    if ``AO.kind = "extended source"``.

    :type: :py:class:`antares.context.ESContext`
    """

    PS = None
    """PS (Point Source) context object. PS attributes are available only
    if ``AO.kind = "point source"``.

    :type: :py:class:`antares.context.PSContext`
    """

    def __init__( self, parent, astro_id=None, init_from_db=False,
                  replica_id=None, replica_num=None ):
        """Replica is initialized with its 'parent' (a camera alert) and
        associated astro object (optional)."""
        self.CA = parent.CA
        self.LA = parent.LA
        self.parent = parent
        self.ra = self.parent.ra
        self.decl = self.parent.decl
        self.astro_id = astro_id
        self.ID = replica_id
        self.num = replica_num

        # conn = pymysql.connect(host='localhost', user='root',
        #                        passwd='', db='antares_demo')
        # cursor = conn.cursor()
        # query = """select ReplicaNumber from AlertReplica where AlertID={0}""".format(parent.ID)
        # cursor.execute( query )
        # replica_num = len(cursor.fetchall()) + 1
        
        if init_from_db == False:
            ## Assign Replica ID.
            # query = """select ReplicaID from AlertReplica"""
            # cursor.execute( query )
            # rows = cursor.fetchall()
            # self.ID = len( rows )
            # conn.close()
            self.flushed2DB = False
            self.num = replica_num
        else:
            #self.ID = replica_id
            self.flushed2DB = True
            self.num = replica_num

        #conn.close()
        ## Populate AR context.
        self.AR = ARContext( self.ID )

        if self.astro_id != None:
            self.AR.HasAstroObject.value = 1
            ## Populate AR context.
            self.AO = AOContext( astro_id )

    def __str__( self ):
        return 'Alert replica {0} belonged to camera alert {1}\n{2}\n{3}'.format(
            self.ID, self.parent.ID, self.AR, self.AO )

    def createReplica( self ):
        """
        Create a replica of the current alert replica.
        """
        #print( 'replica num = ', self.num )
        #self.parent.replica_counter = self.num + 1
        return self.parent.createReplica( astro_id=self.astro_id )

    def divert( self, annotation ):
        """
        Divert the alert replica.

        :param string annotation: a short description of why the alert replica  is diverted.
        """
        ## Just call parent's divert
        self.parent.divert( annotation )

    def mark_as_rare( self, annotation ):
        """
        Mark the alert as a rare alert.

        :param string annotation: a short description of why the alert is rare.
        """
        self.parent.mark_as_rare( annotation )

    def commit( self ):
        """
        Commit the alert replica to Locus-aggregated Alerts DB.
        """
        conn = pymysql.connect( host='127.0.0.1', user='root',
                                passwd='', db='antares_demo' )
        cur = conn.cursor()
        if self.flushed2DB == False:
            if self.astro_id != None:
                query = """select * from AstroObject where AstroObjectID={0}""".format(self.astro_id)
                cur.execute( query )
                if len(cur.fetchall()) == 0:
                    sql_insert = """insert into AstroObject values({0}, "{1}", {2}, {3}, {4})""".format( self.astro_id,
                                                                                                         "SDSS", self.astro_id,
                                                                                                         1, self.parent.locus_id )
                    cur.execute( sql_insert )
                
                sql_insert = """insert into AlertReplica(ReplicaID,ReplicaNumber,AlertID,AstroObjectID,LocusID) \
                values({0}, {1}, {2}, {3}, {4})""".format( self.ID, self.num, self.parent.ID,
                                                           self.astro_id, self.parent.locus_id )
            else:
                sql_insert = """insert into AlertReplica(ReplicaID,ReplicaNumber,AlertID,LocusID) \
                values({0}, {1}, {2}, {3})""".format( self.ID, self.num, self.parent.ID, self.parent.locus_id )

            cur.execute( sql_insert )

            self.flushed2DB = True

        self.AR.commit( cur )
        if self.astro_id != None:
            self.AO.commit( cur )

        conn.commit()

class AlertCombo( CameraAlert ):
    """
    Represents an alert combo which consists of a set of alert replicas
    together with associated astro objects. It is a sub-class of CameraAlert.
    Beyond contexts available for CameraAlert,
    an alert combo is also associated with CB context objects.
    Combo is initialized with a set of alert replicas.

    :param: alert_replicas (:py:class:`list`): a list of :py:class:`AlertReplica`
    """
    
    CB = None
    """CB (Combo) context object. CB attributes are only visible during
    per-combo processing.

    :type: :py:class:`antares.context.CBContext`
    """

    def __init__( self, alert_replicas ):
        """Combo is initialized with a set of alert replicas."""
        pass


class AstroObject:
    """
    Represents an astro object.
    """
    
    def __init__( self ):
        pass

