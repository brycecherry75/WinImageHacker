import argparse, struct, sys, os, ctypes, csv, BMPoperations

ImageHeaderSize_Type1 = 0x0C
ImageHeaderSize_Type2 = 0x28
PaletteSize_2Colour_Type1 = int(3 * 2)
PaletteSize_16Colour_Type1 = int(3 * 16)
PaletteSize_256Colour_Type1 = int(3 * 256)
PaletteSize_2Colour_Type2 = int(4 * 2)
PaletteSize_16Colour_Type2 = int(4 * 16)
PaletteSize_256Colour_Type2 = int(4 * 256)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--exefile", help="EXE file to patch")
  parser.add_argument("--listfile", help="File with locations of images")
  args = parser.parse_args()
  exefilename = args.exefile
  listfilename = args.listfile

  ValidParameters = True

  if not args.exefile:
    ValidParameters = False
    print("ERROR: EXE file with images not specified")
  elif not os.path.isfile(exefilename):
    ValidParameters = False
    print("ERROR: File", exefilename, "not found")
  if not args.listfile:
    ValidParameters = False
    print("ERROR: File with locations of images not specified")
  elif not os.path.isfile(listfilename):
    ValidParameters = False
    print("ERROR: File", listfilename, "not found")

  if ValidParameters == True:
    exefilesize = os.path.getsize(exefilename)
    exefilebuffer = (ctypes.c_byte * exefilesize)()
    exefile = open(exefilename, 'rb')
    exefilebuffer = exefile.read(exefilesize)
    patchedexefilebuffer = (ctypes.c_byte * exefilesize)()
    for BytesToTransfer in range (exefilesize):
      patchedexefilebuffer[BytesToTransfer] = exefilebuffer[BytesToTransfer]
    exefile.close()

    fields = []
    rows = []
    ImagesCounted = 0
    with open(listfilename, 'r') as csvfile:
      ResourceEntryReader = csv.reader(csvfile)
      for row in ResourceEntryReader:
        rows.append(row)
        ImagesCounted = ResourceEntryReader.line_num

      for row in rows[:ImagesCounted]:
        for col in row:
          ValidParamters = True
          value = ("%10s"%col)
          value = value.split(sep=None, maxsplit=6)
          HeaderStart = int(value[0])
          Width = int(value[1])
          Height = int(value[2])
          BitDepth = int(value[3])
          ImageType = int(value[4])
          BMPfileName = value[5]

          if os.path.isfile(BMPfileName):
            BMPfileSize = os.path.getsize(BMPfileName)
            BMPbuffer = (ctypes.c_byte * BMPfileSize)()
            BMPfile = open(BMPfileName, 'rb')
            BMPbuffer = BMPfile.read(BMPfileSize)

            ErrorCode = BMPoperations.CheckValidFormat(BMPbuffer)

            if ErrorCode != BMPoperations.ERROR_NONE:
              ValidParameters = False
              print("Error in", BMPfile, "- code", ErrorCode, "- refer to BMPoperations.py for definition")

            if ValidParameters == True:
              StartOfImage_origin = BMPoperations.GetStartOfImage(BMPbuffer)
              StartOfImage_destination = HeaderStart
              PaletteEntries = (1 << BitDepth)
              BMPpalette = (ctypes.c_byte * (PaletteEntries * 3))()
              Palette_destination = HeaderStart
              ImageSize = (BMPfileSize - StartOfImage_origin)

              ValidBitDepth = True

              if ImageType == 1:
                Palette_destination += ImageHeaderSize_Type1
                StartOfImage_destination += ImageHeaderSize_Type1
                if BitDepth == 1:
                  StartOfImage_destination += PaletteSize_2Colour_Type1
                elif BitDepth == 4:
                  StartOfImage_destination += PaletteSize_16Colour_Type1
                elif BitDepth == 8:
                  StartOfImage_destination += PaletteSize_256Colour_Type1
                elif BitDepth != 16 and BitDepth != 24:
                  ValidBitDepth = False
              elif ImageType == 2:
                Palette_destination += ImageHeaderSize_Type2
                StartOfImage_destination += ImageHeaderSize_Type2
                if BitDepth == 1:
                  StartOfImage_destination += PaletteSize_2Colour_Type2
                elif BitDepth == 4:
                  StartOfImage_destination += PaletteSize_16Colour_Type2
                elif BitDepth == 8:
                  StartOfImage_destination += PaletteSize_256Colour_Type2
                elif BitDepth != 16 and BitDepth != 24:
                  ValidBitDepth = False
              else:
                ValidParameters = False
                print("Unsupported image type for", BMPfileName, "in", listfilename)
              if ValidBitDepth == False:
                ValidParameters = False
                print("Unsupported image bit depth for", BMPfileName, "in", listfilename)

              if Width != BMPoperations.ReadXresolution(BMPbuffer):
                ValidParameters = False
                print("Width to, listfilename, mismatch in", BMPfile)
              if Height != BMPoperations.ReadYresolution(BMPbuffer):
                ValidParameters = False
                print("Height to, listfilename, mismatch in", BMPfile)
              if BitDepth != BMPoperations.ReadBitDepth(BMPbuffer):
                ValidParameters = False
                print("Bit depth to, listfilename, mismatch in", BMPfile)

              if ValidParameters == True:
                print("Patching executable with", BMPfileName)
                if (BitDepth == 8 or BitDepth == 4 or BitDepth == 1) and ImageType == 1:
                  BMPpalette = BMPoperations.ReadPalette(BMPpalette, BMPbuffer)
                  for PaletteEntriesToTransfer in range (PaletteEntries):
                    for Subpixel in range (3):
                      patchedexefilebuffer[(Palette_destination + (3 * PaletteEntriesToTransfer) + Subpixel)] = BMPpalette[((PaletteEntriesToTransfer * 3) + (3 - Subpixel - 1))]

                elif (BitDepth == 8 or BitDepth == 4 or BitDepth == 1) and ImageType == 2:
                  BMPpalette = BMPoperations.ReadPalette(BMPpalette, BMPbuffer)
                  for PaletteEntriesToTransfer in range (PaletteEntries):
                    for Subpixel in range (3):
                      patchedexefilebuffer[(Palette_destination + (4 * PaletteEntriesToTransfer) + Subpixel)] = BMPpalette[((PaletteEntriesToTransfer * 3) + (3 - Subpixel - 1))]

                for BytesToTransfer in range (ImageSize):
                  patchedexefilebuffer[(StartOfImage_destination + BytesToTransfer)] = BMPbuffer[(StartOfImage_origin + BytesToTransfer)]

            BMPfile.close()

    patchedexefile = open(exefilename, 'wb')
    patchedexefile.write(patchedexefilebuffer)
    patchedexefile.close()
    print("Image patch complete")