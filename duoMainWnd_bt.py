#!/usr/bin/python
# coding=utf8

__author__ = 'vin@misday.com'

import os, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from main_ui import *
from downloader_ui import *
from pyvin import ux
from duoSpider import Special
from duoMain import Duokan, Downloader, Config

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class MainWindow(QMainWindow):
    tsize = (20, 20)

    (COLUMN_ID, COLUMN_TITLE, COLUMN_AUTHOR, COLUMN_LINK, COLUMN_PROGRESS) = range(0, 5)
    COLUMNS_WIDTH = [50, 200, 200, 200, 200, 100]

    def __init__(self):
        self.duokan = Duokan()
        self.conf = Config()

        self.tag = MainWindow.__name__
        super( MainWindow, self ).__init__()

        self.ui= Ui_MainWindow()
        self.ui.setupUi(self)
        self.setupPopup()

        self.bindSignal()

        self.powerOff = False

    def setupPopup(self):
        self.ui.tableWidget_books.addAction(self.ui.action_list_view_in_browser)
        self.ui.tableWidget_books.addAction(self.ui.action_list_download)
        self.ui.tableWidget_books.addAction(self.ui.action_list_remove)
        self.ui.tableWidget_books.addAction(self.ui.action_list_merge)
        self.ui.tableWidget_books.addAction(self.ui.action_list_crop)
        self.ui.tableWidget_books.addAction(self.ui.action_list_rename)

    def bindSignal(self):
        QtCore.QObject.connect(self, QtCore.SIGNAL("when_information(QString, QString)"), self.do_message)
        QtCore.QObject.connect(self, QtCore.SIGNAL("when_item_progress(QString, QString)"), self.do_itemProgress)
        QtCore.QObject.connect(self, QtCore.SIGNAL("when_add_book(QString, QString, QString, QString, bool, bool)"), self.appendItem)

    def appendItem(self, id, title='', author='', link='', freed=False, done=False):
        row = self.ui.tableWidget_books.rowCount()
        self.when_add_book(row)

        item = QTableWidgetItem(id)
        self.ui.tableWidget_books.setItem(row, MainWindow.COLUMN_ID, item)

        item = QTableWidgetItem(title)
        self.ui.tableWidget_books.setItem(row, MainWindow.COLUMN_TITLE, item)

        item = QTableWidgetItem(author)
        self.ui.tableWidget_books.setItem(row, MainWindow.COLUMN_AUTHOR, item)

        item = QTableWidgetItem(link)
        self.ui.tableWidget_books.setItem(row, MainWindow.COLUMN_LINK, item)

        # item = QTableWidgetItem(progress)
        item = QProgressBar(self)
        item.setRange(0, 100)
        item.setValue(0)
        item.setTextVisible(True)
        item.setMaximumHeight(15)
        item.setTextDirection(QtGui.QProgressBar.TopToBottom)
        self.ui.tableWidget_books.setCellWidget(row, MainWindow.COLUMN_PROGRESS, item)

        # if freed:
        #     self.list.SetItemBackgroundColour(row, MainWindow.BG_FREED)
        # if done:
        #     self.list.SetItemBackgroundColour(row, MainWindow.BG_DOWN)

        self.adjustListWidth()

    def adjustListWidth(self):
        self.ui.tableWidget_books.resizeColumnsToContents()
        # self.list.SetColumnWidth(MainWindow.COLUMN_NUM, wx.LIST_AUTOSIZE)
        # self.list.SetColumnWidth(MainWindow.COLUMN_ID, wx.LIST_AUTOSIZE)
        # self.list.SetColumnWidth(MainWindow.COLUMN_TITLE, wx.LIST_AUTOSIZE)
        # self.list.SetColumnWidth(MainWindow.COLUMN_AUTHOR, wx.LIST_AUTOSIZE)
        # self.list.SetColumnWidth(MainWindow.COLUMN_LINK, wx.LIST_AUTOSIZE)
        # self.list.SetColumnWidth(MainWindow.COLUMN_PROGRESS, wx.LIST_AUTOSIZE)

    # set download column progress
    def setProgress(self, row, prog):
        if row < self.ui.tableWidget_books.rowCount():
            item = self.ui.tableWidget_books.cellWidget(row, MainWindow.COLUMN_PROGRESS)
            item.setValue(prog)

    # for duoSpider
    def cbAddUrl(self, event, url):
        self.when_special_url(url)

    # for duoSpider
    def cbAddBook(self, event, id, title, author, link):
        notFreed = self.duokan.addBook(id, title, author, link)
        download = self.duokan.isDownload(id)
        self.when_add_book_info(id, title, author, link, (not notFreed), download)

    def startDownload(self):
        if self.downloadRow < self.ui.tableWidget_books.rowCount():
            id = self.ui.tableWidget_books.item(self.downloadRow, MainWindow.COLUMN_ID).text().toUtf8()
            proxy = self.conf.getProxy()
            self.down = Downloader(id, id, proxy[0], proxy[1], proxy[2])
            self.down.bind(Downloader.EVT_START, self.cbStart)
            self.down.bind(Downloader.EVT_STOP,  self.cbStop)
            self.down.bind(Downloader.EVT_LOG,   self.cbLog)
            self.down.bind(Downloader.EVT_PROG,  self.cbProgress)
            self.down.start()

    # for downloader
    def cbStart(self, event):
        self.when_itemProgress(self.downloadRow, 100)
        self.when_progress(0)

    # for downloader
    def cbStop(self, event):
        self.when_itemProgress(self.downloadRow, 100)
        self.when_progress(100)
        # self.list.SetItemBackgroundColour(self.downloadIdx, MainWindow.BG_DOWN)

        # start next
        self.downloadRow += 1
        self.startDownload()

        if self.downloadRow >= self.ui.tableWidget_books.rowCount():
            if self.powerOff:
                os.system('shutdown -t 60 -f -s')

    # for downloader
    def cbLog(self, event, str):
        self.when_logging(str)

    # for downloader
    def cbProgress(self, event, prog):
        self.when_progress(prog)

### signals and slots
    # signals
    def when_logging(self, logStr):
        self.emit(QtCore.SIGNAL("when_logging(QString)"), logStr)

    def when_special_url(self, url):
        self.emit(QtCore.SIGNAL("when_special_url(QString)"), url)

    def when_status(self, text):
        self.emit(QtCore.SIGNAL("when_status(QString)"), text)
    def when_add_book(self, row):
        self.emit(QtCore.SIGNAL("when_add_book(int)"), row)

    def when_del_book(self, row):
        self.emit(QtCore.SIGNAL("when_del_book(int)"), row)

    def when_progress(self, prog):
        self.emit(QtCore.SIGNAL("when_progress(int)"), prog)

    # self defined signal##############################################################################################
    def when_information(self, text, title=''):
        self.emit(QtCore.SIGNAL("when_information(QString, QString)"), text, title)
        self.emit(QtCore.SIGNAL("when_status(QString)"), '%s --> %s' % (title, text))

    def when_itemProgress(self, row, prog):
        self.emit(QtCore.SIGNAL("when_item_progress(int, int)"), row, prog)

    def when_add_book_info(self, id, title, author, link, freed=False, done=False):
        self.emit(QtCore.SIGNAL("when_add_book(QString, QString, QString, QString, bool, bool)"),
                  _fromUtf8(id), _fromUtf8(title), _fromUtf8(author), _fromUtf8(link), freed, done)

    # slots
    def do_update(self):
        self.when_progress(10)
        proxy = self.conf.getProxy()
        special = Special(proxy[0], proxy[1], proxy[2])
        special.bind(Special.EVT_FIND_LINK, self.cbAddUrl)
        special.bind(Special.EVT_FIND_BOOK, self.cbAddBook)
        special.start()
        self.when_progress(100)

    def do_download_all(self):
        self.downloadRow = 0
        self.startDownload()

    def do_open_special_in_browser(self):
        self.duokan.openInNewTab(self.ui.lineEdit_specialUrl.text().toUtf8())

    def do_open_books_folder(self):
        '''open books/new folder'''
        self.duokan.openNewFolder()

    def do_clean_tmp_folder(self):
        self.duokan.cleanTmp()
        self.when_information( 'Finished', 'Clear tmp folder')

    def do_rename_all(self):
        self.duokan.renameAll()
        self.when_information('Finished', 'Rename All')

    def do_crop_book(self):
        file_wildcard = "Pdf files (*.pdf)"
        filePath = QFileDialog.getOpenFileName(self, 'Open file to crop', _fromUtf8(os.path.join(os.getcwd(), 'books')), _fromUtf8(file_wildcard))
        if filePath:
            self.duokan.cropSingle(str(filePath.toUrf8()))
            self.when_information( 'Finished!', 'Crop single')

    def do_merge_book(self):
        filePath = QFileDialog.getExistingDirectory(self, 'Open file to crop', _fromUtf8(os.path.join(os.getcwd(), 'tmp')))
        if filePath:
            print filePath.toUtf8()
            self.duokan.mergeSingle(str(filePath.toUtf8()))
            self.when_information('Finished!', 'Merge single')

    def do_crop_4print(self):
        file_wildcard = "Pdf files (*.pdf)"
        filePath = QFileDialog.getOpenFileName(self, 'Open file to crop for printing', _fromUtf8(os.path.join(os.getcwd(), 'books')), _fromUtf8(file_wildcard))
        if filePath:
            self.duokan.crop4Print(str(filePath.toUrf8()))
            self.when_information( 'Finished!', 'Crop for printing')

    def do_crop_4kindle(self):
        file_wildcard = "Pdf files (*.pdf)"
        filePath = QFileDialog.getOpenFileName(self, 'Open file to crop for printing', _fromUtf8(os.path.join(os.getcwd(), 'books')), _fromUtf8(file_wildcard))
        if filePath:
            self.duokan.crop4Kindle(filePath)
            self.when_information( 'Finished!', 'Crop for kindle')

    def on_power_off_setting(self, powerOff):
        self.powerOff = powerOff
        # print powerOff

    def do_destroyed(self):
        print 'destroyed'

    def do_list_view_in_browser(self):
        ''' open link in browser '''
        row = self.ui.tableWidget_books.currentRow()
        if row != -1:
            url = self.ui.tableWidget_books.item(row, MainWindow.COLUMN_LINK).text().toUtf8()
            self.duokan.openInNewTab(url)

    def do_list_download(self):
        '''download a book'''
        row = self.ui.tableWidget_books.currentRow()
        if row >=0 and row < self.ui.tableWidget_books.rowCount():
            id = self.ui.tableWidget_books.item(row, MainWindow.COLUMN_ID).text().toUtf8()
            title = self.ui.tableWidget_books.item(row, MainWindow.COLUMN_TITLE).text().toUtf8()
            dlg = DownloaderDlg(self, self.conf, title)
            dlg.setId(id)
            dlg.setName(id)
            dlg.show()
        else:
            dlg = DownloaderDlg(self, self.conf)
            dlg.show()

    def do_list_remove(self):
        ''' delete an item '''
        row = self.ui.tableWidget_books.currentRow()
        if row != -1:
            self.when_del_book(row)

    def do_list_merge(self):
        row = self.ui.tableWidget_books.currentRow()
        if row != -1:
            id = self.ui.tableWidget_books.item(row, MainWindow.COLUMN_ID).text().toUtf8()
            self.duokan.merge(id)
            self.when_information('merge finished')

    def do_list_crop(self):
        row = self.ui.tableWidget_books.currentRow()
        if row != -1:
            id = self.ui.tableWidget_books.item(row, MainWindow.COLUMN_ID).text().toUtf8()
            self.duokan.crop(id)
            self.when_information('crop finished')

    def do_list_rename(self):
        ''' rename a item from id to title '''
        row = self.ui.tableWidget_books.currentRow()
        if row != -1:
            id = self.ui.tableWidget_books.item(row, MainWindow.COLUMN_ID).text().toUtf8()
            title = self.ui.tableWidget_books.item(row, MainWindow.COLUMN_TITLE).text().toUtf8()
            self.duokan.rename(id, title)
            self.when_information('rename finished')

    def do_list_dclick(self, row, col):
        url = self.ui.tableWidget_books.item(row, MainWindow.COLUMN_LINK).text().toUtf8()
        self.duokan.openInNewTab(url)

    # self defined slots ###############################################################################################
    def do_message(self, text, title=''):
        QtGui.QMessageBox.information(self, title, text)

    def do_itemProgress(self, row, prog):
        self.setProgress(row, prog)

class DownloaderDlg(QDialog):
    def __init__(self, parent=None, conf=None, tt=''):
        super(DownloaderDlg, self).__init__(parent)

        self.conf = conf

        self.ui= Ui_Dialog()
        self.ui.setupUi(self)
        self.when_title(tt)

        self.downloader = None

    def start(self):
            title = self.windowTitle().toUtf8()
            bid = self.ui.lineEdit_id.text().toUtf8()
            name = self.ui.lineEdit_name.text().toUtf8()

            self.when_message('Title: %s' % title)
            self.when_message('ID: %s' % bid)
            self.when_message('Name: %s' % name)
            self.when_message('downloading...')
            self.when_message('---------')

            proxy = self.conf.getProxy()
            self.downloader = Downloader(bid, name, proxy[0], proxy[1], proxy[2])
            self.downloader.bind(Downloader.ON_STOP, self.cbStop)
            self.downloader.bind(Downloader.EVT_LOG, self.cbLog)
            self.downloader.bind(Downloader.EVT_PROG, self.cbProgress)
            self.downloader.start()

    def stop(self):
        if self.downloader:
            self.downloader.stop()
            self.downloader = None

    def cbStop(self, event):
        self.when_progress(100)
        self.downloader = None

    def cbLog(self, event, msgStr):
        self.when_message(msgStr)

    def cbProgress(self, event, prog):
        self.when_progress(prog)

    def setId(self, id):
        self.when_id(id)
    def setName(self, name):
        self.when_name(name)

#### slots & signals ##################################################################################################
    def do_start(self, checked):
        ''' start download process '''
        if checked:
            print 'checked'
            # self.start()
        else:
            print 'unchecked'
            # self.stop()

    def do_stop(self):
        ''' stop download process '''
        print 'destroy'
        self.stop()

    def when_id(self, id):
        self.emit(QtCore.SIGNAL('when_id(QString)'), _fromUtf8(id))
    def when_name(self, name):
        self.emit(QtCore.SIGNAL('when_name(QString)'), _fromUtf8(name))
    def when_progress(self, prog):
        self.emit(QtCore.SIGNAL('when_progress(int)'), prog)
    def when_message(self, msgStr):
        self.emit(QtCore.SIGNAL('when_message(QString)'), _fromUtf8(msgStr))
    def when_title(self, title):
        self.emit(QtCore.SIGNAL('when_title(QString)'), _fromUtf8(title))

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()