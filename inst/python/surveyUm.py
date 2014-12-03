import os
import glob
import re
import bisect
import csv
import praat


### Function Definitions


### Functions for identifying textgrids to analyse


def getStreetDirs(datastore):
    '''List licit directories of site study data'''

    streetDirs = [x for x in glob.glob(os.path.join(datastore, "PH*"))\
                    if os.path.isdir(x)]

    return(streetDirs)

def listTextGrids(streetDirs):
    '''List the target textgrids in the site study directories'''

    tglist = []
    for street in streetDirs:
        #print(street)
        speakerDirs = [x for x in glob.glob(os.path.join(street, "*"))\
                         if os.path.isdir(x)]

        for speaker in speakerDirs:
            speakerStem = re.sub(r'-[A-Za-z]+$', '', os.path.basename(speaker))
            validTextGrid = re.compile(speakerStem + \
                                       '-([ABCD]+-)?[A-Za-z]+(_fixed)?\.TextGrid')

            tgfiles = glob.glob(os.path.join(speaker,"*.TextGrid"))
            tgfiles = [x for x in tgfiles if validTextGrid.search(x)]

            if len(tgfiles) == 1:
                tglist.append(tgfiles[0])

            elif len(tgfiles) > 1:
                fixed_tg = [x for x in tgfiles if "_fixed" in x]
                if len(fixed_tg) == 1:
                    tglist.append(fixed_tg[0])
                else:
                    print tgfiles
                    print "Too many TextGrids"
    return(tglist)


### A simple utility function that works like the Praat version

def getIntervalAtTime(intervalTier, time):
    '''Return the index of an interval at a given time'''

    startTimes = [x.xmin() for x in intervalTier]

    index = bisect.bisect(startTimes, time)-1
    return(index)


### Functions for scanning through textgrids and identifying small pauses

def findNextSp(intervalTier, counter, mindur):
    '''Given an interval, find the index of the previous sp 
    of duration greater or equal to mindur'''
    maxIndex = len(intervalTier)-1
    if counter+1 > maxIndex:
        return(counter)
    elif intervalTier[counter+1].mark() != "sp":
        counter = findNextSp(intervalTier, counter+1, mindur)
    elif intervalTier[counter+1].mark() == "sp" and \
        intervalTier[counter+1].xmax()-intervalTier[counter+1].xmin() < mindur:
        counter = findNextSp(intervalTier, counter+1, mindur)

    else:
        return(counter+1)

    return(counter)

def findPreviousSp(intervalTier, counter, mindur):
    '''Given an interval, find the index of the previous sp 
    of duration greater or equal to mindur'''
    if counter-1 < 0:
        return(counter)
    elif intervalTier[counter-1].mark() != "sp":
        counter = findPreviousSp(intervalTier, counter-1, mindur)
    elif intervalTier[counter-1].mark() == "sp" and \
        intervalTier[counter-1].xmax()-intervalTier[counter-1].xmin() < mindur:
        counter = findPreviousSp(intervalTier, counter-1, mindur)

    else:
        return(counter-1)

    return(counter)

def findSpStreak(intervalTier, counter):
    '''Find the beginning and end of an sp streak'''
    maxInterval = len(intervalTier)-1
    if counter+1 > maxInterval:
        return(counter)
    elif intervalTier[counter+1].mark() == "sp" or\
         "{" in intervalTier[counter+1].mark():
        counter = findSpStreak(intervalTier, counter+1)
    else:
        return(counter)
    return(counter)



#### Preprocessing of the word tier

def cleanTier(intervalTier):
    '''Collapse adjacent SP and {} intervals'''

    newTier = praat.IntervalTier()

    counter = 0
    while counter+1 < len(intervalTier):
        #print(counter)
        thisInterval = intervalTier[counter]
        if thisInterval.mark() == "sp" or "{" in thisInterval.mark():
            newcounter = findSpStreak(intervalTier, counter)
            lastInterval = intervalTier[newcounter]
            newInterval = praat.Interval(mark = "sp", 
                                         xmin = thisInterval.xmin(),
                                         xmax = lastInterval.xmax())
            newTier.append(newInterval)

            counter = newcounter + 1
        else:
            newInterval = praat.Interval(mark = thisInterval.mark(),
                                         xmin = thisInterval.xmin(),
                                         xmax = thisInterval.xmax())
            newTier.append(newInterval)
            counter += 1
    return(newTier)




def scanTextGrid(tgfile):
    '''Scan a textgrid for "UM" and "UH", and return data'''

    tg = praat.TextGrid()
    tg.read(tgfile)

    originalPhoneTier = tg[0]
    originalWordTier = tg[1]
    newWordTier = cleanTier(originalWordTier)
    newPhoneTier = cleanTier(originalPhoneTier)

    outData = []
    nwords = 0

    for i in range(len(newWordTier)):
        if newWordTier[i].mark() != "sp":
            nwords += 1

        if newWordTier[i].mark() in ["UM", "UH"]:
            if newWordTier[i-1].mark() == "AND":
                outWord = "AND_"+newWordTier[i].mark()
            else:
                outWord = newWordTier[i].mark()

            if newWordTier[i].mark() == "UM" and newWordTier[i+1].mark() == "UH":
            	print "\tum_uh"
                outWord = "UM_UH"
            elif newWordTier[i].mark() == "UH" and newWordTier[i-1].mark()=="UM":
                continue

            startTime = newWordTier[i].xmin()
            endTime = newWordTier[i].xmax()

            vowelIndex = getIntervalAtTime(originalPhoneTier, startTime + 0.001)
            vowelStart = originalPhoneTier[vowelIndex].xmin()
            vowelEnd = originalPhoneTier[vowelIndex].xmax()


            if newWordTier[i].mark() == "UM":
                nasalStart = originalPhoneTier[vowelIndex+1].xmin()
                nasalEnd = originalPhoneTier[vowelIndex+1].xmax()
            else:
                nasalStart = None
                nasalEnd = None

            nextSegIndex = getIntervalAtTime(newPhoneTier, endTime + 0.001)
            if nextSegIndex + 1 > len(newPhoneTier):
                nextSeg = None
                nextSegStart = None
                nextSegEnd = None
            else:
                nextSeg = newPhoneTier[nextSegIndex].mark()
                nextSegStart = newPhoneTier[nextSegIndex].xmin()
                nextSegEnd = newPhoneTier[nextSegIndex].xmax()



            #print(str(newWordTier[i]))
            prevSpIndex = findPreviousSp(newWordTier, i, 0.2)
            prevSpInterval = newWordTier[prevSpIndex]

            chunkStart = prevSpInterval.xmax()

            nextSpIndex = findNextSp(newWordTier, i, 0.2)
            nextSpInterval = newWordTier[nextSpIndex]

            chunkEnd = nextSpInterval.xmin()

            outData.append([outWord, 
                            startTime, endTime, 
                            vowelStart, vowelEnd, 
                            nasalStart, nasalEnd,
                            nextSeg, nextSegStart, nextSegEnd, 
                            chunkStart, chunkEnd])

    outData = [x + [nwords] for x in outData]
    return(outData)




def runScan(tglist, outfile, header):
    '''Run the scan of the tgfiles and write the data'''

    outfile = open(outfile, "wb")
    outwriter = csv.writer(outfile, delimiter = "\t") 
    outwriter.writerow(header)

    for tgfile in tglist:
        print(tgfile)   
        fileBase = os.path.basename(tgfile)
        idstring = re.sub("(PH[0-9]+-[0-9]+-[0-9]+-).*", "\\1", fileBase)
        umData = scanTextGrid(tgfile)

        

        outData = [x+[idstring] for x in umData]

        outwriter.writerows(outData)



### Main Program Begins Here


streetDirs = getStreetDirs("/Volumes/jfruehwa/PNC")
tglist = listTextGrids(streetDirs)

header = ["word", 
          "start_time", "end_time", 
          "vowel_start", "vowel_end",
          "nasal_start", "nasal_end",
          "next_seg", "next_seg_start", "next_seg_end",
          "chunk_start", "chunk_end",
          "nwords",
          "idstring"]

runScan(tglist, "../extdata/PNC_uh_um.txt", header)



