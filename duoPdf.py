
__author__ = 'vin@misday.com'

import sys, os, traceback
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from pyvin.core import Log

class DuoPdf:
    def __init__(self, scr = None):
        self.TAG = DuoPdf.__name__
        pass

    @staticmethod
    def crop(dest, src, left, top, bottom, right):
        Log.i(DuoPdf.__name__, 'cropping file [%s]' % (src, ))
        margin = (left, top, bottom, right)

        srcFile = file(src, 'rb')
        srcPdf = PdfFileReader(srcFile)
        destPdf = PdfFileWriter()

        for page in srcPdf.pages:
            box = page.mediaBox

            # print '%d %d %d %d' % (box.getLowerLeft_x(), box.getLowerLeft_y(), box.getUpperRight_x(), box.getUpperRight_y())
            box.upperRight = (box.getUpperRight_x() - margin[2], box.getUpperRight_y() - margin[3])
            box.lowerLeft  = (box.getLowerLeft_x()  + margin[0], box.getLowerLeft_y()  + margin[1])

            destPdf.addPage(page)
        Log.i(DuoPdf.__name__, 'saving to file [%s]...' % (dest, ))
        destFile = file(dest, 'wb')
        destPdf.write(destFile)
        destFile.close()
        srcFile.close()
        Log.i(DuoPdf.__name__, 'done')

    @staticmethod
    def crop2(dest, src, margin1, margin2):
        Log.i(DuoPdf.__name__, 'cropping file [%s]' % (src, ))

        srcFile = file(src, 'rb')
        srcPdf = PdfFileReader(srcFile)
        destPdf = PdfFileWriter()

        index = 1
        for page in srcPdf.pages:
            box = page.mediaBox

            if index != 1:
                if index % 2 == 1: #odd
                    margin = margin1
                else: #even
                    margin = margin2
                # print '%d %d %d %d' % (box.getLowerLeft_x(), box.getLowerLeft_y(), box.getUpperRight_x(), box.getUpperRight_y())
                box.upperRight = (box.getUpperRight_x() - margin[2], box.getUpperRight_y() - margin[3])
                box.lowerLeft  = (box.getLowerLeft_x()  + margin[0], box.getLowerLeft_y()  + margin[1])

            destPdf.addPage(page)
            index += 1
        Log.i(DuoPdf.__name__, 'saving to file [%s]...' % (dest, ))
        destFile = file(dest, 'wb')
        destPdf.write(destFile)
        destFile.close()
        srcFile.close()
        Log.i(DuoPdf.__name__, 'done')

    @staticmethod
    def cropWH(dest, src, destWidth, destHeight):
        Log.i(DuoPdf.__name__, 'cropping file [%s]' % (src, ))

        srcFile = file(src, 'rb')
        srcPdf = PdfFileReader(srcFile)
        destPdf = PdfFileWriter()

        for page in srcPdf.pages:
            box = page.mediaBox

            width = box.getUpperRight_x() - box.getUpperRight_x()
            height = box.getUpperRight_y() - box.getLowerLeft_y()
            box.upperRight = (destWidth, box.getUpperRight_y() - (height - destHeight) / 2)
            box.lowerLeft  = (0, (height - destHeight) / 2)

            destPdf.addPage(page)
        Log.i(DuoPdf.__name__, 'saving to file [%s]...' % (dest, ))
        destFile = file(dest, 'wb')
        destPdf.write(destFile)
        destFile.close()
        srcFile.close()
        Log.i(DuoPdf.__name__, 'done')

    @staticmethod
    def merge(dest, srcDir):
        '''merge pdf files in srcDir'''
        if os.path.exists(srcDir) and os.path.isdir(srcDir):
            files = os.listdir(srcDir)
            if len(files) > 0:
                merger = PdfFileMerger()
                position = 0
                for f in files:
                    Log.i(DuoPdf.__name__, 'merge file [%s]' % (f, ))
                    filePath = os.path.join(srcDir, f)
                    if (os.path.isfile(filePath)):
                        try:
                            srcFileHdl = open(filePath, 'rb')
                            merger.merge(position=position, fileobj=srcFileHdl)
                        except:
                            Log.w(DuoPdf.__name__, 'merge [%s] failed' % (filePath))
                            traceback.print_exc()
                    else:
                        Log.i(DuoPdf.__name__, 'skip file [%s]' % (filePath,))
                    position += 1
                Log.i(DuoPdf.__name__, 'save to file [%s]...' % (dest, ))
                destFileStream = file(dest, 'wb')
                merger.write(destFileStream)
                destFileStream.close()
                Log.i(DuoPdf.__name__, 'done')
            else:
                Log.w(DuoPdf.__name__, 'no file in [%s] to merge' % (srcDir))
        else:
            Log.w(DuoPdf.__name__, 'dir [%s] not exist.' % (srcDir,))

if __name__ == '__main__':
    src = sys.argv[1]

    # dest = src[:-4] + '.cropped.pdf'
    # duoPdf = DuoPdf(src)
    # duoPdf.cropWH(dest, 500, 666)

    # DuoPdf.duoMerge(src)
    # DuoPdf.duoCrop(src)
    DuoPdf.duoCropForPrint(src)


