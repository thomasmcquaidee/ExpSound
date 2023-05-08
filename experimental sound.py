#import libraries needed to run
from pydub import AudioSegment
from datetime import datetime
import os, ffmpeg

#get current time, to work out how long it takes to run later
startTime = datetime.now()

#directory of your sample library
libraryPath = "/Users/thomasmcquaid/SAMPLE LIBRARY"

#setup various counters, and the "combinedAudio" variable where we store the current chunk
numberOfFiles = 0
filesAdded = 0
chunkCounter = 0
errorCounter = 0
combinedAudio = AudioSegment.empty()

#walk through all the subfolders in the sample library, count how many files can be added to the artifact
for root, dirs, files in os.walk(libraryPath):
    for file in files:
        if file.endswith(".mp3") or file.endswith(".wav") or file.endswith(".aif") or file.endswith(".flac"):
            numberOfFiles = numberOfFiles + 1

print(numberOfFiles, "files in directory")

#main chunk generator
for root, dirs, files in os.walk(libraryPath):
    for file in files:
        try:
            #check if the file type is correct
            if (file.endswith(".mp3") or file.endswith(".wav") or file.endswith(".aif") or file.endswith(".flac")) and filesAdded <= numberOfFiles:
                sample = AudioSegment.from_file(os.path.join(root, file))
                
                #append the current file to the chunk
                combinedAudio += sample
                filesAdded = filesAdded + 1

                #print status to user
                print("\n")
                print("file name  : ", file)
                print("file num   : ", filesAdded, " / ", numberOfFiles)
                print("percentage : ", round((filesAdded/numberOfFiles)*100, 2), "% complete") 

                #check the chunk length. this is really important as the chunk is stored in RAM, so if it gets too large you'll have memory issues
                #if chunk is longer than 20 minutes, export it and add it's name to a list (needed for FFmpeg later)
                if (len(combinedAudio) > 1200000) or (filesAdded == numberOfFiles):
                    with open ("export-%s.mp3" % chunkCounter, "wb") as f:
                        combinedAudio.export(f, format="mp3")

                    with open("list.txt", "a") as listFile:
                        listFile.write("file 'export-%s.mp3'" % chunkCounter)
                        listFile.write("\n")

                    chunkCounter = chunkCounter + 1
                    combinedAudio = AudioSegment.empty()
        except:
            #if there's any issues with current file, add the file name to error.txt to tell user it couldn't be added.
            #ableton files tend to throw errors a lot, they have some sort of copy protection, I got around this by converting them temporeraly to WAV files
            errorCounter = errorCounter + 1
        
            with open("error.txt", "a") as errorFile:
                errorFile.write(file)
                errorFile.write("\n")


#once all chunks are created, get FFmpeg to stream the files together
ffmpegInput = ffmpeg.input("list.txt", f="concat")
ffmpegOutput = ffmpeg.output(ffmpegInput, "output.mp3", c="copy")
ffmpeg.run(ffmpegOutput)

#cleanup - delete all the chunk files + list
for i in range(0, chunkCounter, 1): 
    os.remove("export-%s.mp3" % i)

os.remove("list.txt")

print("\n\n\n")

#calculate and display how long it took to run + how many errors encountered
timeDifference = datetime.now() - startTime
elapsedHours = int(timeDifference.total_seconds() / 3600)
elapsedMinutes = int((timeDifference.total_seconds() % 3600) / 60)

print(f"program took {elapsedHours} hours {elapsedMinutes} minutes to run")
print(errorCounter, "errors")