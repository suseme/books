
__author__ = 'vin@misday.com'

import sys, os, traceback
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from pyvin.core import Log

from pdfrw import PdfReader, PdfWriter

if sys.platform == 'win32':
    pass
elif sys.platform == 'linux2':
    pass

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
                for i,f in enumerate(files):
                    Log.i(DuoPdf.__name__, 'merge file [%s]' % (f, ))
                    filePath = os.path.join(srcDir, f)
                    if (os.path.isfile(filePath)):
                        try:
                            srcFileHdl = open(filePath, 'rb')
                            merger.merge(position=i, fileobj=srcFileHdl)
                        except:
                            Log.w(DuoPdf.__name__, 'merge [%s] failed' % (filePath))
                            traceback.print_exc()
                    else:
                        Log.i(DuoPdf.__name__, 'skip file [%s]' % (filePath,))
                Log.i(DuoPdf.__name__, 'save to file [%s]...' % (dest, ))
                destFileStream = file(dest, 'wb')
                merger.write(destFileStream)
                destFileStream.close()
                Log.i(DuoPdf.__name__, 'done')
            else:
                Log.w(DuoPdf.__name__, 'no file in [%s] to merge' % (srcDir))
        else:
            Log.w(DuoPdf.__name__, 'dir [%s] not exist.' % (srcDir,))

    @staticmethod
    def clean(srcDir):
        if os.path.exists(srcDir) and os.path.isdir(srcDir):
            files = os.listdir(srcDir)
            if len(files) > 0:
                for i,f in enumerate(files):
                    filePath = os.path.join(srcDir, f)
                    if (os.path.isfile(filePath)):
                        try:
                            DuoPdf.cleanPdf(filePath, filePath)
                        except:
                            Log.w(DuoPdf.__name__, 'clean [%s] failed' % (filePath))
                            traceback.print_exc()
                    else:
                        Log.i(DuoPdf.__name__, 'skip file [%s]' % (filePath,))
            else:
                Log.w(DuoPdf.__name__, 'no file in [%s] to clean' % (srcDir))
        else:
            Log.w(DuoPdf.__name__, 'dir [%s] not exist.' % (srcDir,))


    @staticmethod
    def cleanPdf(srcPath, destPath=''):
        if os.path.exists(srcPath):
            if len(destPath) < 1:
                f, e = os.path.splitext(srcPath)
                destPath = f+'.cln.pdf'

            x = PdfReader(srcPath)
            for i, page in enumerate(x.pages):
                print 'page %05d: ' % i,
                xobjs = page.Resources.XObject
                for okey in xobjs.keys():
                    xobj = xobjs[okey]
                    if DuoPdf.isDel(xobj):
                        # xobj.pop('/SMask')
                        xobjs.pop(okey)
                        # print xobj
                        # print xobj.SMask
                        print '.',
                    else:
                        print '[%sx%s#%s]' % (xobj.Width, xobj.Height, xobj.Length),
                print 'done'
            print '[%s] -> [%s]' % (srcPath, destPath)
            PdfWriter().write(destPath, x)

    @staticmethod
    def isDel(xobj):
        # quickly return
        if not xobj:
            return False
        # print xobj.Filter
        # print type(xobj.Filter)
        # print xobj.ColorSpace
        # print type(xobj.ColorSpace)
        # print xobj.Type
        # print type(xobj.Type)
        # print xobj.Subtype
        # print type(xobj.Subtype)
        # if xobj.Filter != '/DCTDecode':             return False
        # if xobj.ColorSpace != '/DeviceRGB':         return False
        # if xobj.Type != '/XObject':                 return False
        if xobj.BitsPerComponent != '8':             return False
        # if xobj.Subtype != '/Image':                return False

        # special xobject
        # print xobj.Length
        # print xobj.Height
        # print xobj.Width
        if xobj.Length == '1027' and xobj.Height == '160' and xobj.Width == '160':            return True
        if xobj.Length == '1027' and xobj.Height == '160' and xobj.Width == '160':            return True
        if xobj.Length == '667'  and xobj.Height == '160' and xobj.Width == '1'  :            return True
        if xobj.Length == '1027' and xobj.Height == '160' and xobj.Width == '160':            return True
        if xobj.Length == '667'  and xobj.Height == '1'   and xobj.Width == '160':            return True
        if xobj.Length == '667'  and xobj.Height == '160' and xobj.Width == '1'  :            return True
        if xobj.Length == '667'  and xobj.Height == '1'   and xobj.Width == '160':            return True
        if xobj.Length == '1027' and xobj.Height == '160' and xobj.Width == '160':            return True

        if xobj.Length == '7491' and xobj.Height == '188' and xobj.Width == '168':            return True
        if xobj.Length == '1226' and xobj.Height == '16'  and xobj.Width == '45':             return True

        # fall down
        return False

class ReduceSize():
    def __init__(self):
        pass

    def cleanAllInPath(self, srcDir):
        if os.path.exists(srcDir) and os.path.isdir(srcDir):
            files = os.listdir(srcDir)
            num = len(files)
            if num > 0:
                for i, f in enumerate(files):
                    print '%d/%d: %s' % (i, num, f)
                    fileName = self.getCleanedFileName(f)
                    srcPath = os.path.join(srcDir, f)
                    destPath = os.path.join(srcDir, fileName)
                    if (os.path.isfile(srcPath)):
                        if self.isCleanedFile(srcPath):
                            print 'skip [%s]' % srcPath
                        elif self.hasCleaned(srcPath):
                            print 'skip [%s]' % srcPath
                        else:
                            try:
                                DuoPdf.cleanPdf(srcPath, destPath)
                                # print '%s -> ' % srcPath
                                # print destPath
                            except:
                                Log.w(DuoPdf.__name__, 'clean [%s] failed' % (srcPath))
                                traceback.print_exc()
                    else:
                        Log.i(DuoPdf.__name__, 'skip file [%s]' % (srcPath,))
            else:
                Log.w(DuoPdf.__name__, 'no file in [%s] to clean' % (srcDir))
        else:
            Log.w(DuoPdf.__name__, 'dir [%s] not exist.' % (srcDir,))

    def isCleanedFile(self, file):
        fileName, extName = os.path.splitext(file)
        fileName, extName = os.path.splitext(fileName)
        if len(extName) < 1:
            return False
        if extName == '.cln':
            return True
        return False

    def hasCleaned(self, file):
        fileName = self.getCleanedFileName(file)
        if os.path.exists(fileName) and os.path.isfile(fileName):
            return True
        return False

    def getCleanedFileName(self, file):
        fileName, extName = os.path.splitext(file)
        return '%s.cln.pdf' % fileName


if __name__ == '__main__':
    src = sys.argv[1]
    # dest = sys.argv[2]
    # dest = src[:-4] + '.cropped.pdf'
    # duoPdf = DuoPdf(src)
    # duoPdf.cropWH(dest, 500, 666)

    # DuoPdf.duoMerge(src)
    # DuoPdf.duoCrop(src)
    # DuoPdf.duoCropForPrint(src)
    # DuoPdf.cleanPdf(src)
    DuoPdf.cleanAllInPath(src)


