from flask import Flask
from flask import render_template
from flask import Markup
from flask import g
import urllib2, json, sqlite3, base64, os
app = Flask(__name__)


'''
first some static stuff and functions for sqlite stuff
'''

basepath = '/var/www/drmcDash/drmcDash/'

microserviceFile = basepath+'static/microservices-list'




'''
now some static stuff for testing the Archivematica API
'''
amBase = 'http://archivematica.museum.moma.org/api/ingest/status/'
amUser = 'bfino'
amAPIkey = '47a5b3791ef9dad6bdfaf56fe27ff78b71c857cb'
testAIPuuid = '190b6bbc-6a7a-4332-b7fe-b890a57727a2'

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/db')
# def connect_to_database():
#     DATABASE = 'static/transfers.db'
#     return sqlite3.connect(DATABASE)
# def get_db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = connect_to_database()
#     return db
# def index():
#     cur = get_db().execute('SELECT * FROM unit')
#     return render_template('print_items.html', items=cur.fetchall())

@app.route('/')
def pipeline(objectNum=None): 
    with open(microserviceFile, 'r') as f:
        microserviceList = [line.strip() for line in f]
    totalMicroNumbers = len(microserviceList)

    # Pipeline #1
    one_DATABASE = '/usr/lib/archivematica/automation-tools/transfers/transfers.db' # this line will be different for each pipeline
    db = getattr(g, '_database', None)
    db = g._database = sqlite3.connect(one_DATABASE)
    one_cur = db.execute('SELECT * from unit WHERE id = (SELECT max(id) FROM unit)')
    one_lastrow = one_cur.fetchone()
    one_sqliteID = one_lastrow[0]
    one_sqliteUUID = one_lastrow[1]
    one_sqlitePath = one_lastrow[2]
    one_sqliteUnitType = one_lastrow[3]
    one_sqliteStatus = one_lastrow[4]
    one_sqliteMicroservice = one_lastrow[5]
    one_sqliteCurrent = one_lastrow[6]
    one_basename = os.path.basename(str(one_sqlitePath))
    one_pathCompNum, one_pathCompID, one_pathObjectID = one_basename.split('---')
    # if sqliteUUID exists, ping the dashboard API. Use sqliteUnitType to decide which endpoint to hit.
    # else if sqliteUnitType is transfer, say that it is doing the initial rsync. how to calculate progress on this? or at least time elapsed?
    one_tmsreq = json.load(urllib2.urlopen("http://vmsqlsvcs.museum.moma.org/TMSAPI/TmsObjectSvc/TmsObjects.svc/GetTombstoneDataRest/ObjectID/"+one_pathObjectID))
    one_tmsMeta = one_tmsreq['GetTombstoneDataRestIdResult']
    one_image = one_tmsreq["GetTombstoneDataRestIdResult"]["Thumbnail"]
    one_tmsTitle = one_tmsreq["GetTombstoneDataRestIdResult"]["Title"]
    one_tmsComponentreq = json.load(urllib2.urlopen("http://vmsqlsvcs.museum.moma.org/TMSAPI/TmsObjectSvc/TmsObjects.svc/GetComponentDetails/Component/"+one_pathCompID))
    one_tmsComponentMeta = one_tmsComponentreq['GetComponentDetailsResult']
    one_tmsComponentName = one_tmsComponentMeta['ComponentName']
    one_archivematicaReq = json.load(urllib2.urlopen(amBase+one_sqliteUUID+'?username='+amUser+'&api_key='+amAPIkey))
    one_amStatus = one_archivematicaReq['status']
    one_amType = one_archivematicaReq['type']
    one_currentMicro = one_archivematicaReq['microservice']
    one_microserviceList = [] 
    one_currentMicroNumber = microserviceList.index(one_currentMicro)+1
    one_microPercentage = int(float(one_currentMicroNumber) / totalMicroNumbers * 100)


    # Pipeline #2
    two_DATABASE = '/usr/lib/archivematica/automation-tools-2/transfers/transfers.db' # this line will be different for each pipeline
    db = getattr(g, '_database', None)
    db = g._database = sqlite3.connect(two_DATABASE)
    two_cur = db.execute('SELECT * from unit WHERE id = (SELECT max(id) FROM unit)')
    two_lastrow = two_cur.fetchone()
    two_sqliteID = two_lastrow[0]
    two_sqliteUUID = two_lastrow[1]
    two_sqlitePath = two_lastrow[2]
    two_sqliteUnitType = two_lastrow[3]
    two_sqliteStatus = two_lastrow[4]
    two_sqliteMicroservice = two_lastrow[5]
    two_sqliteCurrent = two_lastrow[6]
    two_basename = os.path.basename(str(two_sqlitePath))
    two_pathCompNum, two_pathCompID, two_pathObjectID = two_basename.split('---')
    # if sqliteUUID exists, ping the dashboard API. Use sqliteUnitType to decide which endpoint to hit.
    # else if sqliteUnitType is transfer, say that it is doing the initial rsync. how to calculate progress on this? or at least time elapsed?
    two_tmsreq = json.load(urllib2.urlopen("http://vmsqlsvcs.museum.moma.org/TMSAPI/TmsObjectSvc/TmsObjects.svc/GetTombstoneDataRest/ObjectID/"+two_pathObjectID))
    two_tmsMeta = two_tmsreq['GetTombstoneDataRestIdResult']
    two_image = two_tmsreq["GetTombstoneDataRestIdResult"]["Thumbnail"]
    two_tmsTitle = two_tmsreq["GetTombstoneDataRestIdResult"]["Title"]
    two_tmsComponentreq = json.load(urllib2.urlopen("http://vmsqlsvcs.museum.moma.org/TMSAPI/TmsObjectSvc/TmsObjects.svc/GetComponentDetails/Component/"+two_pathCompID))
    two_tmsComponentMeta = two_tmsComponentreq['GetComponentDetailsResult']
    two_tmsComponentName = two_tmsComponentMeta['ComponentName']
    two_archivematicaReq = json.load(urllib2.urlopen(amBase+two_sqliteUUID+'?username='+amUser+'&api_key='+amAPIkey))
    two_amStatus = two_archivematicaReq['status']
    two_amType = two_archivematicaReq['type']
    two_currentMicro = two_archivematicaReq['microservice']
    two_microserviceList = []
    two_currentMicroNumber = 0
    two_microPercentage = 0
    if two_currentMicro in microserviceList: 
        two_currentMicroNumber = microserviceList.index(two_currentMicro)+1
        two_microPercentage = int(float(two_currentMicroNumber) / totalMicroNumbers * 100)


    # pipeline #3
    three_DATABASE = '/usr/lib/archivematica/automation-tools-3/transfers/transfers.db' # this line will be different for each pipeline
    db = getattr(g, '_database', None)
    db = g._database = sqlite3.connect(three_DATABASE)
    three_cur = db.execute('SELECT * from unit WHERE id = (SELECT max(id) FROM unit)')
    three_lastrow = three_cur.fetchone()
    three_sqliteID = three_lastrow[0]
    three_sqliteUUID = three_lastrow[1]
    three_sqlitePath = three_lastrow[2]
    three_sqliteUnitType = three_lastrow[3]
    three_sqliteStatus = three_lastrow[4]
    three_sqliteMicroservice = three_lastrow[5]
    three_sqliteCurrent = three_lastrow[6]
    three_basename = os.path.basename(str(three_sqlitePath))
    three_pathCompNum, three_pathCompID, three_pathObjectID = three_basename.split('---')
    # if sqliteUUID exists, ping the dashboard API. Use sqliteUnitType to decide which endpoint to hit.
    # else if sqliteUnitType is transfer, say that it is doing the initial rsync. how to calculate progress on this? or at least time elapsed?
    three_tmsreq = json.load(urllib2.urlopen("http://vmsqlsvcs.museum.moma.org/TMSAPI/TmsObjectSvc/TmsObjects.svc/GetTombstoneDataRest/ObjectID/"+three_pathObjectID))
    three_tmsMeta = three_tmsreq['GetTombstoneDataRestIdResult']
    three_image = three_tmsreq["GetTombstoneDataRestIdResult"]["Thumbnail"]
    three_tmsTitle = three_tmsreq["GetTombstoneDataRestIdResult"]["Title"]
    three_tmsComponentreq = json.load(urllib2.urlopen("http://vmsqlsvcs.museum.moma.org/TMSAPI/TmsObjectSvc/TmsObjects.svc/GetComponentDetails/Component/"+three_pathCompID))
    three_tmsComponentMeta = three_tmsComponentreq['GetComponentDetailsResult']
    three_tmsComponentName = three_tmsComponentMeta['ComponentName']
    three_archivematicaReq = json.load(urllib2.urlopen(amBase+three_sqliteUUID+'?username='+amUser+'&api_key='+amAPIkey))
    three_amStatus = three_archivematicaReq['status']
    three_amType = three_archivematicaReq['type']
    three_currentMicro = three_archivematicaReq['microservice']
    three_microserviceList = [] 
    three_currentMicroNumber = microserviceList.index(three_currentMicro)+1
    three_microPercentage = int(float(three_currentMicroNumber) / totalMicroNumbers * 100)


    counting_db = basepath+'static/metrics.db' # this line will be different for each pipeline
    db = getattr(g, '_database', None)
    db = g._database = sqlite3.connect(counting_db)
    counting_cur = db.execute('SELECT * from counting')

    labels = []
    preIngest = []
    runComponent = []
    readyForIngest = []
    artworkBacklog = []
    mpaBacklog = []
    preIngestIsilon = []
    readyForIngest2 = []

    for row in counting_cur:
        labels.append(row[0])
        preIngest.append(row[1])
        runComponent.append(row[2])
        readyForIngest.append(row[3])
        artworkBacklog.append(row[4])
        mpaBacklog.append(row[5])
        preIngestIsilon.append(row[6])
        readyForIngest2.append(row[7])

    labels = json.dumps(labels)
    labels = Markup(labels)

    mpaBacklog = [0 if v is None else v for v in mpaBacklog]
    preIngestIsilon = [0 if v is None else v for v in preIngestIsilon]
    readyForIngest2 = [0 if v is None else v for v in readyForIngest2]

    return render_template('dashboard.html',
        labels=labels,
        preIngest = preIngest,
        runComponent = runComponent,
        readyForIngest = readyForIngest,
        artworkBacklog = artworkBacklog,
        mpaBacklog = mpaBacklog,
        preIngestIsilon = preIngestIsilon,
        readyForIngest2 = readyForIngest2,
        one_objectNum=one_tmsMeta,
        one_AIP=one_sqliteUUID,
        one_archivematicaReq=one_archivematicaReq,
        one_img=one_image,
        one_tmsTitle=one_tmsTitle,
        one_tmsComponentName=one_tmsComponentName,
        one_currentMicroNumber=one_currentMicroNumber,
        one_totalMicroNumbers=totalMicroNumbers,
        one_microPercentage=one_microPercentage,
        one_currentMicro=one_currentMicro,
        one_sqliteUnitType=one_sqliteUnitType,
        one_sqliteMicroservice=one_sqliteMicroservice,
        one_sqliteStatus=one_sqliteStatus,
        one_pathCompNum=one_pathCompNum,
        one_pathCompID=one_pathCompID,
        one_pathObjectID=one_pathObjectID,
        one_amType=one_amType,
        one_amStatus=one_amStatus,
        two_objectNum=two_tmsMeta,
        two_AIP=two_sqliteUUID,
        two_archivematicaReq=two_archivematicaReq,
        two_img=two_image,
        two_tmsTitle=two_tmsTitle,
        two_tmsComponentName=two_tmsComponentName,
        two_currentMicroNumber=two_currentMicroNumber,
        two_totalMicroNumbers=totalMicroNumbers,
        two_microPercentage=two_microPercentage,
        two_currentMicro=two_currentMicro,
        two_sqliteUnitType=two_sqliteUnitType,
        two_sqliteMicroservice=two_sqliteMicroservice,
        two_sqliteStatus=two_sqliteStatus,
        two_pathCompNum=two_pathCompNum,
        two_pathCompID=two_pathCompID,
        two_pathObjectID=two_pathObjectID,
        two_amType=two_amType,
        two_amStatus=two_amStatus,
        three_objectNum=three_tmsMeta,
        three_AIP=three_sqliteUUID,
        three_archivematicaReq=three_archivematicaReq,
        three_img=three_image,
        three_tmsTitle=three_tmsTitle,
        three_tmsComponentName=three_tmsComponentName,
        three_currentMicroNumber=three_currentMicroNumber,
        three_totalMicroNumbers=totalMicroNumbers,
        three_microPercentage=three_microPercentage,
        three_currentMicro=three_currentMicro,
        three_sqliteUnitType=three_sqliteUnitType,
        three_sqliteMicroservice=three_sqliteMicroservice,
        three_sqliteStatus=three_sqliteStatus,
        three_pathCompNum=three_pathCompNum,
        three_pathCompID=three_pathCompID,
        three_pathObjectID=three_pathObjectID,
        three_amType=three_amType,
        three_amStatus=three_amStatus
        )



if __name__ == '__main__':
    app.run(debug=True)
