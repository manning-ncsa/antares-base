"""
Configurations for Antares project.
"""

import numpy
import pymysql
from antares.conf import settings

## Path to the astro catalog data used for demo
demo_data_path = '../demo-data'

## Base properties under CA context.
CA_base_properties = {
    'RA' : (float, 'Right ascension'),
    'Decl' : (float, 'Declination'),
    'Magnitude' : (float, 'Logarithmic measure of the brightness of an alert'),
    'MagnitudeErr' : (float, 'Error of magnitude of an alert'),
    'DeltaMagnitude' : (float, 'Absolute value of change of magnitude between two most observations'),
}

## Derived properties under CA context.
CA_derived_properties = {
    'P' : (float, 'Best fit period'),
    'A' : (float, 'Light curve amplitude'),
    'mmed' : (float, 'Median LINEAR magnitude'),
    'stdev' : (float, 'standard deviation of LINEAR magnitudes'),
    'kurt' : (float, 'kurtosis in LINEAR light curves'),
    'rarityVPDF': (float, 'Rarity calculated by VPDF')
    #'skew' : (float, 'skewness in LINEAR light curves'),
}

## Base properties under AR context.
AR_base_properties = {
    'HasAstroObject' : (int, 'Associated with an astro object or not'),
    'SourceAstroObjectTable' : (str, 'The name of source astro-object table'),
}

## Base properties under CA context.
AO_base_properties = {
    'petroMag_u' : (float, 'petroMag_u', 6),
    'petroMag_g' : (float, 'petroMag_g', 7),
    'petroMagErr_u' : (float, 'petroMagErr_u', 16),
    'petroMagErr_g' : (float, 'petroMagErr_g', 17),
    'var_flag' : (int, 'petroMagErr_g', 150),
    #'RA' : (float, 'Right ascension', 1),
    #'Decl' : (float, 'Declination', 2),
    #'oType' : (int, 'SDSS object type', 3),
    #'nS' : (int, 'not saturated flag', 4),
    #'rExt' : (float, 'r-band extinction from the SFD map', 5),
    #'u' : (float, 'magnitude generated by u-band', 6),
    #'g' : (float, 'magnitude generated by g-band', 7),
    #'r' : (float, 'magnitude generated by r-band', 8),
    #'i' : (float, 'magnitude generated by i-band', 9),
    #'z' : (float, 'magnitude generated by z-band', 10),
    #'uErr' : (float, 'u-magnitude error', 11),
    #'gErr' : (float, 'g-magnitude error', 12),
    #'rErr' : (float, 'r-magnitude error', 13),
    #'zErr' : (float, 'z-magnitude error', 14),
    #'iErr' : (float, 'i-magnitude error', 15),
}

BASE_PROP = 0     # indicate base property
DERIVED_PROP = 1  # indicate derived property

## We can generate upto this many camera alerts for the demo.
total_num_alerts = 7194

def GetDBConn():
    try:
        conn = pymysql.Connect(host=settings.db_host_local, user=settings.db_user,
                               passwd=settings.db_pwd, db=settings.db_name)
    except:
        conn = pymysql.Connect(host=settings.db_host_remote, user=settings.db_user,
                               passwd=settings.db_pwd, db=settings.db_name)

    return conn
