# WinImageHacker
Extract and patch images from Windows 16/32 bit executable files e.g. card games - as of the time of writing, ResourceHacker currently does not support 16 bit Windows executable files

Requires BMP_AVI_operations: http://github.com/brycecherry75/BMP_AVI_operations

## Usage
First, generate a listing of images:

python ExtractImages.py -h

Edit the images (for icons, use the image without a corrupted top half and for cursors, use the image having a height which is double its width) while maintaining colour depth and dimensions (the palette if present can be edited if desired), rename and/or remove the image files including in the listing file if desired and then patch them:

python PatchImages.py -h