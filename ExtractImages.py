import argparse, struct, sys, os, ctypes, csv, BMPoperations

ImageHeaderSize_Type1 = 0x0C
ImageHeaderSize_Type2 = 0x28
PaletteSize_2Colour_Type1 = int(3 * 2)
PaletteSize_16Colour_Type1 = int(3 * 16)
PaletteSize_256Colour_Type1 = int(3 * 256)
PaletteSize_2Colour_Type2 = int(4 * 2)
PaletteSize_16Colour_Type2 = int(4 * 16)
PaletteSize_256Colour_Type2 = int(4 * 256)

def ReadWordInt(address, ArrayIn):
  return ((ArrayIn[address] & 0xFF) | ((ArrayIn[(address + 1)] & 0xFF) << 8))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--exefile", help="File with images")
  parser.add_argument("--listfile", help="File to store locations of images")
  args = parser.parse_args()
  if args.exefile:
    exefilename = args.exefile
    if args.listfile:
      listfilename = args.listfile
      if os.path.isfile(exefilename):
        exefilesize = os.path.getsize(exefilename)
        exefilebuffer = (ctypes.c_byte * exefilesize)()
        exefile = open(exefilename, 'rb')
        exefilebuffer = exefile.read(exefilesize)

        with open(listfilename, 'w', newline='') as csvfile:
          ListFileWriter = csv.writer(csvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
          ImageCount = 0
          ImageTypesFound = 0
          print("Searching for Type 1 images")
          for FileAddress in range (int(exefilesize / 4)):
            if ((FileAddress * 4) + 0x0C) <= exefilesize and ReadWordInt(((FileAddress * 4) + 0x00), exefilebuffer) == 12 and ReadWordInt(((FileAddress * 4) + 0x02), exefilebuffer) == 0  and ReadWordInt(((FileAddress * 4) + 0x08), exefilebuffer) == 1:
              BitDepth = ReadWordInt(((FileAddress * 4) + 0x0A), exefilebuffer)
              if BitDepth == 24 or BitDepth == 16 or BitDepth == 8 or BitDepth == 4 or BitDepth == 1:
                Width = ReadWordInt(((FileAddress * 4) + 0x04), exefilebuffer)
                Height = ReadWordInt(((FileAddress * 4) + 0x06), exefilebuffer)
                FileSize = BMPoperations.CalculateFileSize(Width, Height, BitDepth)
                FileSize -= BMPoperations.CalculatePaletteSize(BitDepth)
                FileSize -= BMPoperations.HeaderSizeBeforePaletteOrImageData
                HeaderSize = ImageHeaderSize_Type1
                if BitDepth == 1:
                  HeaderSize += PaletteSize_2Colour_Type1
                elif BitDepth == 4:
                  HeaderSize += PaletteSize_16Colour_Type1
                elif BitDepth == 8:
                  HeaderSize += PaletteSize_256Colour_Type1
                if FileSize > 0 and Width >= 1 and Height >= 1:
                  if ((FileAddress * 4) + FileSize + HeaderSize) > exefilesize and (Width * 2) == Height: # icon at the end
                    FileSize = int(FileSize / 2)
                    Height = int(Height / 2)
                  if ((FileAddress * 4) + FileSize + HeaderSize) <= exefilesize:
                    ListFileWriter.writerow([(FileAddress * 4)] + [Width] + [Height] + [BitDepth] + [1] + [ImageCount] + ['.bmp'])
                  ImageCount += 1

          Type1ImageCount = ImageCount
          print(Type1ImageCount, "Type 1 images found")

          print("Searching for Type 2 images")
          for FileAddress in range (int(exefilesize / 4)):
            if ((FileAddress * 4) + 0x28) <= exefilesize and ReadWordInt(((FileAddress * 4) + 0x00), exefilebuffer) == 40 and ReadWordInt(((FileAddress * 4) + 0x02), exefilebuffer) == 0 and ReadWordInt(((FileAddress * 4) + 0x06), exefilebuffer) == 0 and ReadWordInt(((FileAddress * 4) + 0x0A), exefilebuffer) == 0 and ReadWordInt(((FileAddress * 4) + 0x0C), exefilebuffer) == 1:
              ByteBeingChecked = 0x16
              BitDepth = 0
              while True:
                if exefilebuffer[((FileAddress * 4) + ByteBeingChecked)] != 0x00:
                  break
                ByteBeingChecked += 1
                if ByteBeingChecked > 0x27:
                  BitDepth = ReadWordInt(((FileAddress * 4) + 0x0E), exefilebuffer)
                  break
              if BitDepth == 24 or BitDepth == 16 or BitDepth == 8 or BitDepth == 4 or BitDepth == 1:
                Width = ReadWordInt(((FileAddress * 4) + 0x04), exefilebuffer)
                Height = ReadWordInt(((FileAddress * 4) + 0x08), exefilebuffer)
                FileSize = BMPoperations.CalculateFileSize(Width, Height, BitDepth)
                FileSize -= BMPoperations.CalculatePaletteSize(BitDepth)
                FileSize -= BMPoperations.HeaderSizeBeforePaletteOrImageData
                HeaderSize = ImageHeaderSize_Type2
                if BitDepth == 1:
                  HeaderSize += PaletteSize_2Colour_Type2
                elif BitDepth == 4:
                  HeaderSize += PaletteSize_16Colour_Type2
                elif BitDepth == 8:
                  HeaderSize += PaletteSize_256Colour_Type2
                if FileSize > 0 and Width >= 1 and Height >= 1:
                  if ((FileAddress * 4) + FileSize + HeaderSize) > exefilesize and (Width * 2) == Height: # icon at the end
                    FileSize = int(FileSize / 2)
                    Height = int(Height / 2)
                  if ((FileAddress * 4) + FileSize + HeaderSize) <= exefilesize:
                    ListFileWriter.writerow([(FileAddress * 4)] + [Width] + [Height] + [BitDepth] + [2] + [ImageCount] + ['.bmp'])
                    ImageCount += 1

          Type2ImageCount = (ImageCount - Type1ImageCount)
          print(Type2ImageCount, "Type 2 images found")

          print("Searching for Type 1 icons")
          for FileAddress in range (int(exefilesize / 4)):
            if ((FileAddress * 4) + 0x0C) <= exefilesize and ReadWordInt(((FileAddress * 4) + 0x00), exefilebuffer) == 12 and ReadWordInt(((FileAddress * 4) + 0x02), exefilebuffer) == 0  and ReadWordInt(((FileAddress * 4) + 0x08), exefilebuffer) == 1:
              BitDepth = ReadWordInt(((FileAddress * 4) + 0x0A), exefilebuffer)
              if BitDepth == 24 or BitDepth == 16 or BitDepth == 8 or BitDepth == 4 or BitDepth == 1:
                Width = ReadWordInt(((FileAddress * 4) + 0x04), exefilebuffer)
                Height = ReadWordInt(((FileAddress * 4) + 0x06), exefilebuffer)
                FileSize = BMPoperations.CalculateFileSize(Width, Height, BitDepth)
                FileSize -= BMPoperations.CalculatePaletteSize(BitDepth)
                FileSize -= BMPoperations.HeaderSizeBeforePaletteOrImageData
                HeaderSize = ImageHeaderSize_Type1
                if BitDepth == 1:
                  HeaderSize += PaletteSize_2Colour_Type1
                elif BitDepth == 4:
                  HeaderSize += PaletteSize_16Colour_Type1
                elif BitDepth == 8:
                  HeaderSize += PaletteSize_256Colour_Type1
                if FileSize > 0 and Width >= 1 and Height >= 1 and (Width * 2) == Height:
                  FileSize = int(FileSize / 2)
                  Height = int(Height / 2)
                  if ((FileAddress * 4) + FileSize + HeaderSize) <= exefilesize:
                    ListFileWriter.writerow([(FileAddress * 4)] + [Width] + [Height] + [BitDepth] + [1] + [ImageCount] + ['.bmp'])
                  ImageCount += 1

          Type1IconCount = (ImageCount - Type1ImageCount - Type2ImageCount)
          print(Type1IconCount, "Type 1 icons found")

          print("Searching for Type 2 icons")
          for FileAddress in range (int(exefilesize / 4)):
            if ((FileAddress * 4) + 0x28) <= exefilesize and ReadWordInt(((FileAddress * 4) + 0x00), exefilebuffer) == 40 and ReadWordInt(((FileAddress * 4) + 0x02), exefilebuffer) == 0 and ReadWordInt(((FileAddress * 4) + 0x06), exefilebuffer) == 0 and ReadWordInt(((FileAddress * 4) + 0x0A), exefilebuffer) == 0 and ReadWordInt(((FileAddress * 4) + 0x0C), exefilebuffer) == 1:
              ByteBeingChecked = 0x16
              BitDepth = 0
              while True:
                if exefilebuffer[((FileAddress * 4) + ByteBeingChecked)] != 0x00:
                  break
                ByteBeingChecked += 1
                if ByteBeingChecked > 0x27:
                  BitDepth = ReadWordInt(((FileAddress * 4) + 0x0E), exefilebuffer)
                  break
              if BitDepth == 24 or BitDepth == 16 or BitDepth == 8 or BitDepth == 4 or BitDepth == 1:
                Width = ReadWordInt(((FileAddress * 4) + 0x04), exefilebuffer)
                Height = ReadWordInt(((FileAddress * 4) + 0x08), exefilebuffer)
                FileSize = BMPoperations.CalculateFileSize(Width, Height, BitDepth)
                FileSize -= BMPoperations.CalculatePaletteSize(BitDepth)
                FileSize -= BMPoperations.HeaderSizeBeforePaletteOrImageData
                HeaderSize = ImageHeaderSize_Type2
                if BitDepth == 1:
                  HeaderSize += PaletteSize_2Colour_Type2
                elif BitDepth == 4:
                  HeaderSize += PaletteSize_16Colour_Type2
                elif BitDepth == 8:
                  HeaderSize += PaletteSize_256Colour_Type2
                if FileSize > 0 and Width >= 1 and Height >= 1 and (Width * 2) == Height:
                  FileSize = int(FileSize / 2)
                  Height = int(Height / 2)
                  if ((FileAddress * 4) + FileSize + HeaderSize) <= exefilesize:
                    ListFileWriter.writerow([(FileAddress * 4)] + [Width] + [Height] + [BitDepth] + [2] + [ImageCount] + ['.bmp'])
                    ImageCount += 1

          Type2IconCount = (ImageCount - Type1ImageCount - Type2ImageCount - Type1IconCount)
          print(Type2IconCount, "Type 2 icons found")


        # remove the unwanted space
        ListFileSize = os.path.getsize(listfilename)
        ListFileBuffer_origin = (ctypes.c_byte * ListFileSize)()
        ListFile_origin = open(listfilename, 'rb')
        ListFileBuffer_origin = ListFile_origin.read(ListFileSize)
        ListFile_origin.close()
        UnwantedSpaceCount = 0
        for ByteToCheck in range (ListFileSize):
          if ListFileBuffer_origin[ByteToCheck] == 0x2E:
            UnwantedSpaceCount += 1
        ListFileBuffer_destination = (ctypes.c_byte * (ListFileSize - UnwantedSpaceCount - 2))()
        UnwantedSpaceCount = 0
        for ByteToTransfer in range (ListFileSize):
          if ByteToTransfer < (ListFileSize - 2):
            if ListFileBuffer_origin[(ByteToTransfer + 1)] != 0x2E:
              ListFileBuffer_destination[(ByteToTransfer - UnwantedSpaceCount)] = ListFileBuffer_origin[ByteToTransfer]
            else:
              UnwantedSpaceCount += 1
        ListFile_destination = open(listfilename, 'wb')
        ListFile_destination.write(ListFileBuffer_destination)
        ListFile_destination.close()       

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
              value = ("%10s"%col)
              value = value.split(sep=None, maxsplit=6)
              HeaderStart = int(value[0])
              Width = int(value[1])
              Height = int(value[2])
              BitDepth = int(value[3])
              ImageType = int(value[4])
              BMPfileName = value[5]

              BMPfileSize = BMPoperations.CalculateFileSize(Width, Height, BitDepth)
              BMPbuffer = (ctypes.c_byte * BMPfileSize)()
              BMPbuffer = BMPoperations.WriteHeader(Width, Height, BitDepth, 2835, 2835, BMPbuffer)
              StartOfImage_destination = BMPoperations.GetStartOfImage(BMPbuffer)
              StartOfImage_origin = HeaderStart
              PaletteEntries = (1 << BitDepth)
              BMPpalette = (ctypes.c_byte * (PaletteEntries * 3))()
              Palette_origin = HeaderStart
              ImageSize = (BMPfileSize - StartOfImage_destination)

              if ImageType == 1:
                Palette_origin += ImageHeaderSize_Type1
                StartOfImage_origin += ImageHeaderSize_Type1
                if BitDepth == 1:
                  StartOfImage_origin += PaletteSize_2Colour_Type1
                elif BitDepth == 4:
                  StartOfImage_origin += PaletteSize_16Colour_Type1
                elif BitDepth == 8:
                  StartOfImage_origin += PaletteSize_256Colour_Type1
              if ImageType == 2:
                Palette_origin += ImageHeaderSize_Type2
                StartOfImage_origin += ImageHeaderSize_Type2
                if BitDepth == 1:
                  StartOfImage_origin += PaletteSize_2Colour_Type2
                elif BitDepth == 4:
                  StartOfImage_origin += PaletteSize_16Colour_Type2
                elif BitDepth == 8:
                  StartOfImage_origin += PaletteSize_256Colour_Type2

              if (BitDepth == 8 or BitDepth == 4 or BitDepth == 1) and ImageType == 1:
                for PaletteEntriesToTransfer in range (PaletteEntries):
                  for Subpixel in range (3):
                    BMPpalette[((PaletteEntriesToTransfer * 3) + (3 - Subpixel - 1))] = exefilebuffer[(Palette_origin + (3 * PaletteEntriesToTransfer) + Subpixel)]
                BMPbuffer = BMPoperations.WritePalette(BMPpalette, BMPbuffer)

              elif (BitDepth == 8 or BitDepth == 4 or BitDepth == 1) and ImageType == 2:
                for PaletteEntriesToTransfer in range (PaletteEntries):
                  for Subpixel in range (3):
                    BMPpalette[((PaletteEntriesToTransfer * 3) + (3 - Subpixel - 1))] = exefilebuffer[(Palette_origin + (4 * PaletteEntriesToTransfer) + Subpixel)]
                BMPbuffer = BMPoperations.WritePalette(BMPpalette, BMPbuffer)

              for BytesToTransfer in range (ImageSize):
                BMPbuffer[(StartOfImage_destination + BytesToTransfer)] = exefilebuffer[(StartOfImage_origin + BytesToTransfer)]

              BMPfile = open(BMPfileName, 'wb')
              BMPfile.write(BMPbuffer)
              BMPfile.close()

        exefile.close()
        print("Image extraction complete")

      else:
        print("ERROR: File", exefilename, "not found")
    else:
      print("ERROR: File to store locations of images not specified")
  else:
    print("ERROR: EXE file with images not specified")