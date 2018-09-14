import time, os, nltk
from flask import Flask, render_template, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_caching import Cache

nltk.download ('all')

cached_locations = None

engine= create_engine("postgres://db/openstreetmap")
DBUSER = 'postgres'
DBPASS = 'postgres'
DBHOST = 'db'
DBPORT = '5432'
DBNAME = 'openstreetmap'



os.system('PGPASSWORD="postgres" pg_restore -h db -p 5432 -U postgres -F t -1 -d openstreetmap data/au_nz_places.tar')

app = Flask(__name__)
# Initialize flask cache
cache=Cache(app, config={'CACHE_TYPE':'simple'})
cache.init_app(app)


# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}'.format(
        user=DBUSER,
        passwd=DBPASS,
        host=DBHOST,
        port=DBPORT,
        db=DBNAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'postgres'


db = SQLAlchemy(app)

db.engine.execute("CREATE EXTENSION IF NOT EXISTS postgis;CREATE EXTENSION IF NOT EXISTS hstore;CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;CREATE EXTENSION IF NOT EXISTS hstore;CREATE SCHEMA IF NOT EXISTS reveal;")





# decorating index function with the app.route with url as /login
@app.route('/')
def index():
    return render_template('geoparse.html')



@app.route('/result',  methods=['POST'])
def parse():
   if request.method == 'POST':
        import os, sys, logging, traceback, codecs, datetime, copy, time, ast, math, re, random, shutil, json
        import geoparsepy.config_helper,geoparsepy.common_parse_lib,geoparsepy.PostgresqlHandler,geoparsepy.geo_parse_lib,geoparsepy.geo_preprocess_lib
        
        global cached_locations
        global indexed_locations
        global indexed_geoms
        global osmid_lookup
        global dictGeomResultsCache 
        osms=[]
        coords=[]
        names=[]
        LOG_FORMAT = ('%(message)s')
        logger = logging.getLogger( __name__ )
        logging.basicConfig( level=logging.INFO, format=LOG_FORMAT )
        logger.info('logging started')

        dictGeospatialConfig = geoparsepy.geo_parse_lib.get_geoparse_config( 
                lang_codes = ['de'],
                logger = logger,
                corpus_dir = None,
                whitespace = u'"\u201a\u201b\u201c\u201d()',
                sent_token_seps = ['\n','\r\n', '\f', u'\u2026'],
                punctuation = """,;\/:+-#~&*=!?""",
                )
        
        databaseHandle = geoparsepy.PostgresqlHandler.PostgresqlHandler( 'postgres', 'postgres', 'db', 5432, 'openstreetmap', 600 )
        dictLocationIDs = {}
        listFocusArea=['au_nz_places']
        for strFocusArea in listFocusArea :
                dictLocationIDs[strFocusArea + '_admin'] = [-1,-1]
                dictLocationIDs[strFocusArea + '_poly'] = [-1,-1]
                dictLocationIDs[strFocusArea + '_line'] = [-1,-1]
                dictLocationIDs[strFocusArea + '_point'] = [-1,-1]

        if cached_locations is None:
            cached_locations = geoparsepy.geo_preprocess_lib.cache_preprocessed_locations( databaseHandle, dictLocationIDs, 'reveal',
            dictGeospatialConfig )


            logger.info( 'number of cached locations = ' + str(len(cached_locations)) )

            databaseHandle.close()

            indexed_locations = geoparsepy.geo_parse_lib.calc_inverted_index( cached_locations, dictGeospatialConfig )
            logger.info( 'number of indexed phrases = ' + str(len(indexed_locations.keys())) )

            indexed_geoms = geoparsepy.geo_parse_lib.calc_geom_index( cached_locations )
            logger.info( 'number of indexed geoms = ' + str(len(indexed_geoms.keys())) )

            osmid_lookup = geoparsepy.geo_parse_lib.calc_osmid_lookup( cached_locations )

            dictGeomResultsCache = {}



        listText = [request.form['parsetext']]
                #u'hello New York, USA its Bill from Bassett calling',
                #u'live on the BBC Victoria Derbyshire is visiting Derbyshire for an exclusive UK interview. Gehmer in Acton Park Schnitzel essen und dann in Aberdare ein Eis aber nur wenn in Zurich noch Licht brennt.',
                

        listTokenSets = []
        listGeotags = []
        for nIndex in range(len(listText)) :
                strUTF8Text = listText[ nIndex ]
                listToken = geoparsepy.common_parse_lib.unigram_tokenize_microblog_text( strUTF8Text, dictGeospatialConfig )
                listTokenSets.append( listToken )
                listGeotags.append( None )

        listMatchSet = geoparsepy.geo_parse_lib.geoparse_token_set( listTokenSets, indexed_locations, dictGeospatialConfig )


        strGeom = 'POINT(-1.4052268 50.9369033)'
        listGeotags[0] = strGeom

        listMatchGeotag = geoparsepy.geo_parse_lib.reverse_geocode_geom( [strGeom], indexed_geoms, dictGeospatialConfig )
        if len( listMatchGeotag[0] ) > 0  :
                for tupleOSMIDs in listMatchGeotag[0] :
                        setIndexLoc = osmid_lookup[ tupleOSMIDs ]
                        for nIndexLoc in setIndexLoc :
                                strName = cached_locations[nIndexLoc][1]
                                #logger.info( 'Reverse geocoded geotag location [index ' + str(nIndexLoc) + ' osmid ' + repr(tupleOSMIDs) + '] = ' + strName )

        for nIndex in range(len(listMatchSet)) :
                logger.info( 'Text = ' + listText[nIndex] )
                listMatch = listMatchSet[ nIndex ]
                strGeom = listGeotags[ nIndex ]
                setOSMID = set([])
                for tupleMatch in listMatch :
                        nTokenStart = tupleMatch[0]
                        nTokenEnd = tupleMatch[1]
                        tuplePhrase = tupleMatch[3]
                        for tupleOSMIDs in tupleMatch[2] :
                                setIndexLoc = osmid_lookup[ tupleOSMIDs ]
                                for nIndexLoc in setIndexLoc :
                                        logger.info( 'Location [index ' + str(nIndexLoc) + ' osmid ' + repr(tupleOSMIDs) + ' @ ' + str(nTokenStart) + ' : ' + str(nTokenEnd) + '] = ' + ' '.join(tuplePhrase) + ' Geometry:' + str(strGeom) )
                                        logger.info(cached_locations[nIndexLoc][4])
                                        names.append(' '.join(tuplePhrase))
                                        osms.append(repr(tupleOSMIDs))
                                        coords.append(cached_locations[nIndexLoc][4])
                                        break
                listLocMatches = geoparsepy.geo_parse_lib.create_matched_location_list( listMatch, cached_locations, osmid_lookup )
                geoparsepy.geo_parse_lib.filter_matches_by_confidence( listLocMatches, dictGeospatialConfig, geom_context = strGeom, geom_cache = dictGeomResultsCache )
                geoparsepy.geo_parse_lib.filter_matches_by_geom_area( listLocMatches, dictGeospatialConfig )
                geoparsepy.geo_parse_lib.filter_matches_by_region_of_interest( listLocMatches, [-148838, -62149], dictGeospatialConfig )
                setOSMID = set([])
                for nMatchIndex in range(len(listLocMatches)) :
                        nTokenStart = listLocMatches[nMatchIndex][1]
                        nTokenEnd = listLocMatches[nMatchIndex][2]
                        tuplePhrase = listLocMatches[nMatchIndex][3]
                        strGeom = listLocMatches[nMatchIndex][4]
                        tupleOSMID = listLocMatches[nMatchIndex][5]
                        dictOSMTags = listLocMatches[nMatchIndex][6]
                        if not tupleOSMID in setOSMID :
                                setOSMID.add( tupleOSMID )
                                listNameMultilingual = geoparsepy.geo_parse_lib.calc_multilingual_osm_name_set( dictOSMTags, dictGeospatialConfig )
                                strNameList = ';'.join( listNameMultilingual )
                                strOSMURI = geoparsepy.geo_parse_lib.calc_OSM_uri( tupleOSMID, strGeom )
                                logger.info( 'Disambiguated Location [index ' + str(nMatchIndex) + ' osmid ' + repr(tupleOSMID) + ' @ ' + str(nTokenStart) + ' : ' + str(nTokenEnd) + '] = ' + strNameList + ' : ' + strOSMURI)

                return render_template('success.html',names=names,osms=osms,coords=coords)



if __name__ == '__main__':
    dbstatus = False
    while dbstatus == False:
        try:
            db.create_all()
        except:
            time.sleep(2)
        else:
            dbstatus = True
   # database_initialization_sequence()
    app.run(debug=True, host='0.0.0.0')
