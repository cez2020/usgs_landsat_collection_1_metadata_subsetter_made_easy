import pandas as pd
import os


def getUSGSCollOneMetadata(csvFile, path, row, tier, cloud, timeFrom, timeTo, previous, missionName):
    print("\nReading raw USGS csv file...\n")
    with open(csvFile) as f:
        fileEncoding = f.encoding
        all_scenes = pd.read_csv(csvFile, encoding=fileEncoding, parse_dates=[
                                 'acquisitionDate'], index_col=['acquisitionDate'])
        print("Image entries in raw dataset:", all_scenes.shape[0], "\n")

    # subset images by location
    wrs_path = path  # Landsat paths
    wrs_row = row  # Landsat rows
    loc_scenes = all_scenes[all_scenes['path'].isin(wrs_path) &
                            all_scenes['row'].isin(wrs_row)]
    print("Location-specific images:", loc_scenes.shape[0], "\n")

    # subset images by tier
    loc_scenes = loc_scenes[loc_scenes['COLLECTION_CATEGORY'] == tier]
    print("Tier", tier[1], "images: ", loc_scenes.shape[0], "\n")

    # subset images by cloud cover
    loc_scenes = loc_scenes[loc_scenes['cloudCover'] <= cloud]
    print("Cloud Cover condition applied. Remaining images:",
          loc_scenes.shape[0], "\n")

    # subset images by date
    # loc_scenes = pd.to_datetime(loc_scenes)
    loc_scenes = loc_scenes.loc[timeFrom:timeTo]
    print("Images between", timeFrom, "and",
          timeTo + ":", loc_scenes.shape[0], "\n")

    # select displayID column
    displayID = loc_scenes['LANDSAT_PRODUCT_ID']

    # select header for output text file (as required by USGS)
    missionID = missionName
    if missionID == "TM":
        missionHeader = "landsat_tm_c1|displayId"
    elif missionID == "ETM":
        missionHeader = "landsat_etm_c1|displayId"
    elif missionID == "L8":
        missionHeader = "landsat_8_c1|displayId"

    # set file names
    fileNameOne = "sceneIDs_%s.txt" % missionHeader[:-10]
    fileNameTwo = "scenes_%s.txt" % missionHeader[:-10]

    # open last scene ID list if given
    if previous != None:
        print("Eliminated repeated images.\n")
        with open(previous) as f:
            fileEncoding = f.encoding
            lastDisplayID = pd.read_csv(
                previous, encoding=fileEncoding)
        # remove repeated scene IDs
        uniqueDisplayID = loc_scenes['Display ID'][~loc_scenes['Display ID'].isin(
            lastDisplayID[missionHeader])].drop_duplicates()
        print("Final image count:", uniqueDisplayID.shape[0], "\n")

        # # save scene ID values in a text file (one per line)
        uniqueDisplayID.to_csv(fileNameOne,
                               header=False, index=False, sep='\n')
    elif previous == None:
        # save scene ID values in a text file (one per line)
        displayID.to_csv(fileNameOne,
                         header=False, index=False, sep='\n')

    # generate text file as output
    with open(fileNameOne, 'r') as readFile:
        with open(fileNameTwo, 'w') as writeFile:
            writeFile.write(missionHeader + '\n')
            for line in readFile:
                writeFile.write(line)

    # remove temp txt file
    os.remove(fileNameOne)

    print("Use the following file as input in USGS API:\n", fileNameTwo, "\n")

#################################
# Enter your own parameters here


# Example: "LANDSAT_OT_C2_L2.csv"
USGScsvFile = "LANDSAT_8_C1.csv"
usgsPaths = [2, 3, 4]                           # Example: [2, 3, 4]
usgsRows = [67, 68, 69]                         # Example: [67, 68, 69]
usgsTier = "T1"                                 # Example: "T1" or "T2"
cloudCover = 10                                 # Example: 15
timeFrom = "2013-01-01"                         # Example: "2021-01-01"
timeTo = "2021-07-01"                           # Example: "2021-07-28"
previousScenes = None                           # Example: "folder/oldScenes.csv" OR None
# previousScenes = "previous/OLDscenes_landsat_ot_c2_l2.txt"
LandsatMission = "L8"
# Mission Options:
# Landsat 4-5 (Thematic Mapper): "TM"
# Landsat 7 (Enhanced Thematic Mapper Plus): "ETM"
# Landsat 8 (OLI/TIRS): "L8"


getUSGSCollOneMetadata(USGScsvFile, usgsPaths,
                       usgsRows, usgsTier, cloudCover, timeFrom, timeTo, previousScenes, LandsatMission)
