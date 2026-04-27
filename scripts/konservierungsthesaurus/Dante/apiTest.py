import requests
import csv
import json
import os
import sys

checksumFileLink = "https://api.dante.gbv.de/export/download/leiza_archlink/Standardexport/checksums.txt"
vocabularyFileLink = "https://api.dante.gbv.de/export/download/leiza_archlink/Standardexport/leiza_archlink__Standardexport.turtle.ttl"

def readChecksumFile(file):
    with open(file, "r") as f:
        checksumTable = list(csv.reader(f))
        ttlRow = checksumTable[9][0]
        ttlColumns = ttlRow.split()
        if ttlColumns[0] == "leiza_archlink__Standardexport.turtle.ttl":
            ttlChecksum = ttlColumns[2]
            return ttlChecksum
        else:
            raise ValueError("Unexspected data in checksums.txt")

# Check if checksum file exists
if os.path.exists("checksums.txt"):
    originalChecksum = readChecksumFile("checksums.txt")
else:
    print("No existing checksum file found - will download new files")
    originalChecksum = None

checkSumFile = requests.get(checksumFileLink)
checkSumFileContent = checkSumFile.text
with open("newChecksums.txt", "w") as file:
    file.write(checkSumFileContent)

newChecksum = readChecksumFile("newChecksums.txt")

if newChecksum == originalChecksum:
    print("No changes in vocabulary file")
    os.remove("newChecksums.txt")
else:
    print("Vocabulary file has changed or no original checksum found")
    print("Replacing checksum.txt with newChecksum.txt")
    os.replace("newChecksums.txt", "checksums.txt")

    # Always download the vocabulary file when checksum changed or was missing
    print("Downloading new vocabulary file")
    vocabularyFile = requests.get(vocabularyFileLink)
    vocabularyFileContent = vocabularyFile.text
    with open("vocabulary.ttl", "w") as file:
        file.write(vocabularyFileContent)

