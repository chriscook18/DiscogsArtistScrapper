# -*- coding: utf-8 -*-

#Random crash? Probably sent too many requests to Discogs for this minute#

import requests, json, time
from pprint import pprint
from datetime import datetime
import dateutil.parser
import pymysql
import pymysql.cursors
import pytz
    
def main(person):
    #Person is their discogs artist ID
    
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',
                                 database='discogs',
                                 cursorclass=pymysql.cursors.DictCursor)
    
    with connection:
        with connection.cursor() as cursor:
     
            url = "https://api.discogs.com/artists/" + str(person) + "/releases"
            
            #First call
            data = callDiscogs(url)
            parseResults(cursor, data, person, connection)
            
            #Get the pagination details
            pagination = data['pagination']
            iPages = pagination['pages']
    
            iPage = 2
            while iPage <= iPages:
                print("page" + str(iPage))
                pageUrl = url+ "?page=" + str(iPage)
                data = callDiscogs(pageUrl)
                parseResults(cursor, data, person, connection)
    
                ++iPage
              
        
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
        
def executeSQLCommand(cursor, sSql):
    ### call the database
    
    #Debug mode
  #  print(sSql)
    cursor.execute(sSql)
    
def createRecord(cursor, release, person, artist, role, bUpdate = False):
    ##Build up some sql
    
    try:
        year = release['year'] 
    except:
        year = 0
        
    try:
        masterid = release['master_id'] 
    except:
        masterid = 0
        
    try:
        country = repr(release['country'])
    except:
        country="''"
        
    try:
        rLabel = release['labels'][0]
        label = repr(rLabel['name'])
        catalogno = repr(rLabel['catno'])
    except:
        label = "''"
        catalogno = "''"
        
        
    print("done " + str(release['id']))
    
    if (bUpdate):
        sSql = "UPDATE `releases` SET `TITLE`=" + repr(release['title']) + ",`ARTIST`=" + repr(artist) + ",`YEAR`=" + str(year)
        sSql += ",`MASTERID`=" + str(masterid) + ",`COUNTRY`=" + country + ", `LASTUPDATEDB`=CURRENT_TIMESTAMP, `LASTUPDATEDISCOGS`=" + repr(release['date_changed'])
        sSql += ", `ROLE`=" + repr(role) + ", `LABEL`=" + label + ",`CATALOGNO`=" + catalogno
        sSql += " WHERE `ID`=" + str(release['id']) + " AND `PERSON`=" + str(person)
 
    else:
        sSql = "INSERT INTO `releases`(`ID`, `PERSON`, `TITLE`, `ARTIST`, `YEAR`, `MASTERID`, `COUNTRY`, `ADDEDTODB`, `LASTUPDATEDB`, `ADDEDTODISCOGS`, `LASTUPDATEDISCOGS`, `ROLE`, `LABEL`, `CATALOGNO`)"
        sSql += " VALUES( "+ str(release['id']) + "," + str(person) + "," + repr(release['title']) + "," + repr(artist) + "," + str(year)
        sSql += "," + str(masterid) + "," +  country  + ",CURRENT_TIMESTAMP,CURRENT_TIMESTAMP," + repr(release['date_added']) + "," + repr(release['date_changed'])
        sSql += "," + repr(role) + "," + label + "," + catalogno
        sSql += ")"

    executeSQLCommand(cursor, sSql)
    
    
def updateRecord(cursor, release, person, artist, role, rExistingEntry):
    #Update the record if necessary    
 

    if(pytz.utc.localize(rExistingEntry['LASTUPDATEDB'])) <= dateutil.parser.isoparse(release['date_changed']):
       #Update record - assuming the tracklisting hasn't changed.
       createRecord(cursor, release, person, artist,role,True)
    else:
        print("skipping - already up to date " + str(release['id']))
    
def doReleaseThingies(cursor, person, artist, role, releaseid)  :
    #Check if it already exists in db
    
    release = callDiscogs("https://api.discogs.com/releases/" + str(releaseid))
    
    
    sSql = "SELECT `ID`, `PERSON`, `LASTUPDATEDB` FROM `releases` WHERE `ID` =" + str(releaseid) + " AND `PERSON` =" + str(person)
    executeSQLCommand(cursor, sSql)
    
    rResult = cursor.fetchone()
    
    #debug
    #print(rResult);
    
    if rResult == None:
        # Create a new record - repr to make strings right format to insert
        createRecord(cursor, release, person, artist, role)
        addSongRows(cursor, release)
    else:
        updateRecord(cursor, release, person, artist, role, rResult)
        
        
def addSongRows(cursor, release):
    
    #Get the first artist if multiple as lazy
    try:
        sAlbumArtist = release['artists'][0]['name']
    except:
        sAlbumArtist = "Various"        
        
    for track in release['tracklist']:
        try:
            sTrackArtist = track['artists'][0]['name']
        except:
            sTrackArtist = sAlbumArtist
            
        sSql = "INSERT INTO `songs`(`RELEASEID`, `SONGTITLE`, `SONGARTIST`) VALUES (" + str(release['id']) + ", " + repr(track['title']) + ", " + repr(sTrackArtist) + ")"
        executeSQLCommand(cursor, sSql)
        
    
        
def parseResults(cursor, data, person, connection):
    
    for release in data['releases']:

        if release['type'] == "master":
            searchMasters(cursor, release, person, connection, data['pagination'])
            
        else:
            doReleaseThingies(cursor, person, release['artist'], release['role'], release['id'])
    
    #Save progress
    connection.commit()
    
def searchMasters(cursor, releaseFromArtist, person, connection, pagination):
    
    url = "https://api.discogs.com/masters/" + str(releaseFromArtist['id']) + "/versions"
    versions = callDiscogs(url)
    searchMastersInternal(versions, cursor, releaseFromArtist, person, connection)
    
    #Get the pagination details
    iPages = pagination['pages']
    if iPages <= 2:
        iPage = 2
        while iPage <= iPages:
            print("Master page " + str(iPage))
            pageUrl = url+ "?page=" + str(iPage)
            versions = callDiscogs(pageUrl)
            searchMastersInternal(versions, cursor, releaseFromArtist, person, connection)
            
            ++iPage
    
    #time.sleep(5)
    
    #Commit what we've done so far
    connection.commit()
    
def searchMastersInternal(versions, cursor, releaseFromArtist, person, connection):
   
     for version in versions['versions']:
        doReleaseThingies(cursor,person, releaseFromArtist['artist'], releaseFromArtist['role'], version['id'])
        
def callDiscogs(url):
    headers = {'User-Agent':'BruceyScrapper/0.1'}
    r = requests.get(url, headers=headers)
    data = r.json()
    
    #Sleep between calls to stop us running over the call rate limit
    time.sleep(3)
       
    return data

if __name__ == '__main__':
    main(100702)
    
    
