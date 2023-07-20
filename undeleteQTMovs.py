import os
import sys
import time

from pathlib import Path

foundHeader = False
headerSub = ""
bufferIn = 0x00
bytesRead = 0
gigsRead = 0
kbRead = 0
mbRead = 0

# File data structure
thisBS = 0
thisType = 0
thisSubType = 0
nextBS = 0
nextType = 0
nextSubType = 0


print(" undeleteQTMovs.py V1.0 ")
print("  Python Version: ", sys.version, "\n")

if (len(sys.argv) != 2):
  print(" Usage: undeleteQTMovs.py [image]")
  exit()

print("  Command: ", sys.argv)
print("  File to Scan: ", sys.argv[1])
print("  Starting...")

try:
  f = open(sys.argv[1], "rb")
except Exception as ex:
  print("!!! An exception was encountered opening the file: ", ex)
  exit()

#####################
# QuickTime Format
# ================
# Address Offset Description
# 00:03   0      Block size (4b integer)
# 04:07   4      Type -- for first block of MOV this must be 'ftyp' (0x66747970)
# 08:0B   8      Sub type -- for MOV type should be 'qt__' (0x71742020)
# 0C:0F   12     ?????
# 
#  Parent 'Atom'
# ...................
# | [Atom Size]
# | 0x0000 (32-bit int) defining Atom size including header and data
# | >> If '0', last Atom in file and it extends to end of file
# | >> If '1', extended field size 64-bit following 'type' field
# |
# | [Type]
# | 0x0000 (32-bit int) defining atom type, typically plain-text characters
# |
# | [Extended Size]
# | 0x00000000 (64-bit int)
# Seek for trials
#
f.seek(573997200,1)
# Read bytes until 'ftyp' is found
while f.readable():
  try:
    # Looking for 'ftyp'
    bytesRead += 1
    bufferIn = f.read(1)
#    print(bufferIn[0])

    if len(bufferIn) < 1:
      print("Reached a zero read lenth at ", f.tell())
      break

    if len(headerSub) == 1:    # so far have 'f'
      if (bufferIn[0] == 0x74):
        headerSub = "ft"
      else:
        headerSub = ""
    elif len(headerSub) == 2:  # so far have 'ft'
      if (bufferIn[0] == 0x79):
        headerSub = "fty"
        #print("Looking close...",flush=True)
      else:
        headerSub = ""
    elif len(headerSub) == 3:  # so far have 'fty'
      if (bufferIn[0] == 0x70):
        headerSub = ""
        # TODO Seek back to block size and read 4B value
        f.seek(-8,1)
        print("Header found at ", f.tell(), flush=True)

        # Parent Atom
        thisBS = f.read(4)
        thisType = f.read(4)
        thisSubType = f.read(4)
        print("Block size ", int.from_bytes(thisBS), "\nType: ", thisType, "\nSub Type: ", thisSubType, flush=True)
        f.seek(-12,1)
        f.seek(int.from_bytes(thisBS),1)

        nextBS = f.read(4)
        nextType = f.read(4)
        nextSubType = f.read(4)
        print("Block size ", int.from_bytes(nextBS), "\nType: ", nextType, "\nSub Type: ", nextSubType, "Loc: ", f.tell(),flush=True)
        if (nextType != b'ftyp') and (nextType != b'moov') and (nextType != b'mdat'):
          continue
        f.seek(-12,1)
 #       f.seek(int.from_bytes(nextBS),1)

        while (nextType == b'ftyp') or (nextType == b'moov') or (nextType == b'mdat') or (nextType == b'free') or (nextType == b'skip') or (nextType == b'wide') or (nextType == b'pnot'):
          f.seek(int.from_bytes(nextBS),1)
          nextBS = f.read(4)
          nextType = f.read(4)
          if (nextBS == 1):
            nextBS = f.read(8)
          else:
            nextSubType = f.read(4)
            f.read(4)
          print("Block size ", int.from_bytes(nextBS), "\nType: ", nextType, "\nSub Type: ", nextSubType, "Loc: ", f.tell(),flush=True)
          f.seek(-16,1)


      else:                      # key is empty
        headerSub = ""
    else:
      if (bufferIn[0] == 0x66):
        headerSub = bufferIn
      else:
        headerSub = ""
    if (bytesRead > 1024*1024*50):
      bytesRead = f.tell()
      gigsRead = bytesRead / (1024*1024*1024)
      mbRead = bytesRead / (1024*1024)
      print(gigsRead," GB Read, ", mbRead, " MB Read", flush=True)
      bytesRead = 0
      #break
#    if (mbRead > 500):
#      print("Finished at ", f.tell())
#      break
  except Exception as ex:
    print("Encountered an exception in the seek loop: ", ex)


try:
  print("Closing the file")
  f.close()
except Exception as ex:
  print("An exception was encountered attempting to close the file handle: ", ex)
