import sys
from PyQt5 import QtGui, QtCore, QtWidgets #, QtWinExtras
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import numpy as np
import os
import cv2
from time import sleep
from scipy import ndimage as nd
import pandas as pd

class Worker(QtCore.QObject):
    saveFinishedSignal = pyqtSignal()
    saveFinishedSignal2 = pyqtSignal()
    progressBarUpdateSignal = pyqtSignal(float)
    progressBarUpdateSignal2 = pyqtSignal(float)
    setCurveDataSignal = pyqtSignal(int,np.ndarray,np.ndarray,np.ndarray,np.ndarray)
    setCurveDataSignal2 = pyqtSignal(int,np.ndarray,np.ndarray,np.ndarray)
    expFinishedSignal = pyqtSignal(list,list,np.ndarray,np.ndarray,np.ndarray,np.ndarray)
    expFinishedSignal2 = pyqtSignal(list,list,np.ndarray,np.ndarray,np.ndarray,np.ndarray,np.ndarray,np.ndarray)
    loadFinishedSignal = pyqtSignal(np.ndarray,np.ndarray,np.ndarray,np.ndarray,list,list,list)
    loadFinishedSignal2 = pyqtSignal(np.ndarray,np.ndarray,np.ndarray,np.ndarray,np.ndarray,np.ndarray,list,list,list)
    scopeTimeoutErrorSignal = pyqtSignal(float)
    
    def __init__(self):
        QtCore.QObject.__init__(self)

class myViewBox(QtWidgets.QWidget):
    def __init__(self,parent,w,h):
        super(myViewBox, self).__init__(parent)
        self.overlay = QtGui.QImage(w,h,QtGui.QImage.Format_RGBA8888)
        self.overlay.fill(QtGui.QColor("transparent"))
    
    def reset(self, w, h):
        self.overlay = QtGui.QImage(w,h,QtGui.QImage.Format_RGBA8888)
        self.overlay.fill(QtGui.QColor("transparent"))
#        painter	= QtGui.QPainter(self.p)
        self.repaint()
#        painter.eraseRect(self.rect())
#        painter.drawPixmap(self.rect(), self.overlay, self.rect())
#        painter.end()

        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
#        painter.begin(self)
        painter.drawImage(self.rect(), self.overlay)
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() and QtCore.Qt.LeftButton and self.drawing:
            painter = QtGui.QPainter(self.overlay)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.SolidLine))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button == QtCore.Qt.LeftButton:
            self.drawing = False
        
class Form(QtWidgets.QMainWindow):
    def __init__(self,w,h):
        QtWidgets.QMainWindow.__init__(self)
#        self.worker = Worker()  # no parent!
#        self.thread = QThread()  # no parent!
        # Connections for asking worker thread to do something
#        self.requestLoadSignal2.connect(self.worker.loadFile2)
#        # Connections for UI thread to do something after worker thread
#        self.worker.saveFinishedSignal.connect(self.finishSave)
##         3 - Move the Worker object to the Thread object
#        self.worker.moveToThread(self.thread)
#         4 - Connect Worker Signals to the Thread slots
#        self.finished.connect(self.thread.quit)
#         5 - Connect Thread started signal to Worker operational slot method
#        self.saveDone.connect(lambda: self.saveLight.setPixmap(blackLED))
#         6 - Start the thread
#        self.thread.start()
        self.setupUi(w,h)
        
    def setupUi(self,w,h):
#        myFloatVal = QtGui.QRegExpValidator(QtCore.QRegExp('[\d]+[.]?[\d]*'))
        
        self.setObjectName('MainWindow')
#        self.setWindowModality(QtCore.Qt.WindowModal)
        self.resize(w, h)
        self.showMaximized()
        self.setMaximumSize(QtCore.QSize(w, h))
        font = QtGui.QFont()
        font.setFamily('Segoe UI')
        font.setPointSize(10)
        self.setFont(font)
        self.setAutoFillBackground(True)
        self.setIconSize(QtCore.QSize(10, 10))
        self.setWindowTitle('Ultrasound Image Processor')
#        self.setWindowIcon(icon)
#        self.taskbarIcon = QtWinExtras.QWinTaskbarButton(self)
#        self.taskbarIcon.setOverlayIcon(icon)
#        self.setIcon(icon)
        
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName('centralwidget')
        self.setCentralWidget(self.centralwidget)
        p = self.centralwidget.palette()
        p.setColor(self.centralwidget.backgroundRole(), QtCore.Qt.black)
        self.centralwidget.setAutoFillBackground(True)
        self.centralwidget.setPalette(p)
        
        self.drawing = False
        self.lastPoint = QtCore.QPoint()
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, int(0.15*w), int(0.9*h)))
        self.groupBox.setObjectName('groupBox')
        try:
            currentFile = os.path.realpath(__file__).replace('\\','/')
        except:
            currentFile = input('Python needs your help determining the location of this script.\nPlease copy the full filepath of this Python script from above,\nthen paste it here using right-click. Then press Enter to begin.\n')
        currentFile = currentFile.replace('\\','/')
        self.scriptdir = currentFile[:currentFile.rfind('/')+1]
#        filedir = scriptdir[:scriptdir.rfind('/',1,len(scriptdir)-2)+1]
        self.dirButton = QtWidgets.QPushButton(self.groupBox)
        self.dirButton.setGeometry(QtCore.QRect(10,10,30,25))
        self.dirButton.setText('Dir')
        self.dirButton.setObjectName('dirButton')
        self.dirField = QtWidgets.QLineEdit(self.groupBox)
        self.dirField.setGeometry(QtCore.QRect(50, 10, int(0.15*w-60), 25))
        self.dirField.setObjectName('dirField')
        self.dirField.setReadOnly(True)
        self.dirField.setText(self.scriptdir)
        self.leftButton = QtWidgets.QPushButton(self.groupBox)
        self.leftButton.setGeometry(QtCore.QRect(int(0.01*w),50,int(0.02*w),int(0.04*h)))
        self.leftButton.setText('<')
        self.leftButton.setObjectName('leftButton')
        self.rightButton = QtWidgets.QPushButton(self.groupBox)
        self.rightButton.setGeometry(QtCore.QRect(int(0.04*w),50,int(0.02*w),int(0.04*h)))
        self.rightButton.setText('>')
        self.rightButton.setObjectName('rightButton')
        self.saveButton = QtWidgets.QPushButton(self.groupBox)
        self.saveButton.setGeometry(QtCore.QRect(int(0.07*w),50,int(0.03*w),int(0.04*h)))
        self.saveButton.setText('Save')
        self.saveButton.setObjectName('saveButton')
        self.clearButton = QtWidgets.QPushButton(self.groupBox)
        self.clearButton.setGeometry(QtCore.QRect(int(0.11*w),50,int(0.03*w),int(0.04*h)))
        self.clearButton.setText('Clear')
        self.clearButton.setObjectName('clearButton')
        self.processButton = QtWidgets.QPushButton(self.groupBox)
        self.processButton.setGeometry(QtCore.QRect(int(0.035*w),100,int(0.08*w),int(0.04*h)))
        self.processButton.setText('Process Stored Images')
        self.processButton.setObjectName('processButton')
        self.imgFormatLabel = QtWidgets.QLineEdit(self.groupBox)
        self.imgFormatLabel.setGeometry(QtCore.QRect(int(0.025*w),200,int(0.05*w),int(0.04*h)))
        self.imgFormatLabel.setText('Image Format')
        self.imgFormatLabel.setObjectName('imgFormatLabel')
        self.imgFormatLabel.setReadOnly(True)
        self.vidFormatLabel = QtWidgets.QLineEdit(self.groupBox)
        self.vidFormatLabel.setGeometry(QtCore.QRect(int(0.085*w),200,int(0.05*w),int(0.04*h)))
        self.vidFormatLabel.setText('Video Format')
        self.vidFormatLabel.setObjectName('vidFormatLabel')
        self.vidFormatLabel.setReadOnly(True)
        self.imgFormatDropDown = QtWidgets.QComboBox(self.groupBox)
        self.imgFormatDropDown.setGeometry(QtCore.QRect(int(0.025*w),250,int(0.05*w),int(0.04*h)))
        self.imgFormatDropDown.addItems(['.jpg','.tif','.png'])
        self.imgFormatDropDown.setObjectName('imgFormatDropDown')
        self.vidFormatDropDown = QtWidgets.QComboBox(self.groupBox)
        self.vidFormatDropDown.setGeometry(QtCore.QRect(int(0.085*w),250,int(0.05*w),int(0.04*h)))
        self.vidFormatDropDown.addItems(['.avi','.mov','.mp4'])
        self.vidFormatDropDown.setObjectName('vidFormatDropDown')
        self.digestVideosButton = QtWidgets.QPushButton(self.groupBox)
        self.digestVideosButton.setGeometry(QtCore.QRect(int(0.05*w),150,int(0.05*w),int(0.04*h)))
        self.digestVideosButton.setText('Digest Videos')
        self.digestVideosButton.setObjectName('digestVideosButton')
        
        saveAction = QtWidgets.QAction('Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveImage)
        self.addAction(saveAction)
        
        prevImage = QtWidgets.QAction('Stop', self)
        prevImage.setShortcut(QtCore.Qt.Key_Left)
        prevImage.triggered.connect(self.prevImage)
        self.addAction(prevImage)
        
        nextImage = QtWidgets.QAction('NextTab', self)
        nextImage.setShortcut(QtCore.Qt.Key_Right)
        nextImage.triggered.connect(self.nextImage)
        self.addAction(nextImage)
        
        exitAction = QtWidgets.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(QtWidgets.qApp.quit)
        self.addAction(exitAction)
        
        self.dirButton.clicked.connect(self.openFileNameDialog)
        self.clearButton.pressed.connect(self.clearDrawing)
        self.leftButton.pressed.connect(self.prevImage)
        self.rightButton.pressed.connect(self.nextImage)
        self.saveButton.pressed.connect(self.saveImage)
        self.processButton.pressed.connect(self.processImages)
        self.digestVideosButton.pressed.connect(self.digestVideos)
        self.loadImageList()
        self.changeImage()
        self.show()
    
    def loadImageList(self):
        filesAndFolders = os.listdir(self.dirField.text())
        self.imgFiles = [fileOrFolder for fileOrFolder in filesAndFolders if self.imgFormatDropDown.currentText() in fileOrFolder]
        self.imgIndex = 0
        
    def loadVideoList(self):
        filesAndFolders = os.listdir(self.dirField.text())
        self.imgFiles = [fileOrFolder for fileOrFolder in filesAndFolders if self.vidFormatDropDown.currentText() in fileOrFolder]
        self.imgIndex = 0
        
    def changeImage(self):
        if len(self.imgFiles) > 0:
            self.image = QtGui.QImage(self.imgFiles[self.imgIndex])
            w,h = self.image.width(), self.image.height()
            if len(self.centralwidget.children()) > 1:
                self.vL.reset(w,h)
                self.vL.setGeometry(QtCore.QRect(500, 50, w,h))
                self.backgroundBox.setPixmap(QtGui.QPixmap(self.image))
            else:
                self.backgroundBox = QtWidgets.QLabel(self.centralwidget)
                self.backgroundBox.setGeometry(QtCore.QRect(500, 50, w,h))
                self.backgroundBox.setPixmap(QtGui.QPixmap(self.image))
                self.backgroundBox.setObjectName('backgroundBox')
                self.vL = myViewBox(self.centralwidget,w,h)
                self.vL.setGeometry(QtCore.QRect(500, 50, w,h))
                self.vL.setObjectName('vL')
    
    def openFileNameDialog(self):
        filedirtemp = QtWidgets.QFileDialog.getExistingDirectory(self,'Select Directory',self.dirField.text())
        if filedirtemp != '':
            filedirtemp2 = filedirtemp.replace('\\','/')
            if filedirtemp2[-1] != '/':
                filedir = filedirtemp2 + '/'
            else:
                filedir = filedirtemp2
            self.dirField.setText(filedir)
            self.loadImageList()
            self.loadVideoList()
    
    def clearDrawing(self):
        w,h = self.image.width(), self.image.height()
        self.vL.reset(w,h)
        
        
    def prevImage(self):
        if self.imgIndex > 0:
            self.imgIndex -= 1
        else:
            self.imgIndex = len(self.imgFiles) - 1
        self.changeImage()
    
    def nextImage(self):
        if len(self.imgFiles) > self.imgIndex + 1:
            self.imgIndex += 1
        else:
            self.imgIndex = 0
        self.changeImage()
    
    def saveImage(self):
        self.backgroundBox.clear()
        self.backgroundBox.repaint()
        screenshot = screen.grabWindow(self.backgroundBox.winId())
        f = self.imgFormatDropDown.currentText()
        screenshot.save(self.imgFiles[self.imgIndex].replace(f,'-mask' + f), f.replace('.',''))
        self.nextImage()
    
    def processImages(self):
        if len(self.imgFiles) > 0:
            answerz = ['Error applying mask']*len(self.imgFiles)
            imgFormat = self.imgFormatDropDown.currentText()
            for z,file in enumerate(self.imgFiles):
                if os.path.isfile(file.replace(imgFormat,'-mask' + imgFormat)):
                    mask = cv2.imread(file.replace(imgFormat,'-mask'+ imgFormat))[:,:,2] < 10
                    region,n = nd.label(mask)
                    c = np.zeros(n,np.uint32)
                    for i in range(n):
                        c[i] = np.count_nonzero(region==i+1)
                    if n == 2:
                        img = cv2.imread(file)[:,:,0]
                        maskedimg = np.ma.array(img,mask=region==(np.argmin(c)+1))
                        answerz[z] = maskedimg.mean()
                else:
                    answerz[z] = 'Mask file not found.'
            currentFile = os.path.realpath(__file__).replace('\\','/')
            excelFileName = currentFile.replace(os.path.basename(currentFile),'') + 'Image Processing Output - 1.xlsx'
            a = 1
            while os.path.isfile(excelFileName):
                a += 1
                excelFileName = excelFileName.replace('Output - ' + str(a-1) + '.xlsx','Output - '+str(a) + '.xlsx')
            writer = pd.ExcelWriter(excelFileName)
            df = pd.DataFrame(self.imgFiles)
            df.to_excel(writer, startrow=0, startcol = 0, sheet_name='Image Processing', header = ['Filename'], index=False, engine='xlsxwriter')
            df2 = pd.DataFrame(answerz)
            df2.to_excel(writer, startrow=0, startcol = 1, sheet_name='Image Processing', header = ['Average Brightness Value inside mask'], index=False, engine='xlsxwriter')
            writer.sheets['Image Processing'].set_column('A:A',50,None)
            writer.sheets['Image Processing'].set_column('B:B',40,None)
            writer.save()
        
    def digestVideos(self):
        nFiles = len(self.vidFiles)
        if nFiles > 0:
            vidFormat = self.vidFormatDropDown.currentText()
            imgFormat = self.imgFormatDropDown.currentText()
            totalFrames = 0
            for fileNum,file in self.vidFiles:
                print('Processing file ' + str(fileNum+1) + ' of ' + str(nFiles) + ': ' + file)
                cap = cv2.VideoCapture(self.scriptdir+file)
                vidDir = self.scriptdir+file.replace(vidFormat,'/')
                if not os.path.isdir(vidDir):
                    os.mkdir(vidDir)
                h, w, nFrames = int(cap.get(4)), int(cap.get(3)), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                totalFrames += nFrames
                cap.set(cv2.CAP_PROP_CONVERT_RGB,False)
                ret = True
                i = 0
                frames = np.zeros((450,580,nFrames),dtype='uint8')
                while i < nFrames:
                    ret,frame = cap.read()
                    if ret:
                        frames[:,:,i] = frame[92:542,143:723,0]
                        cv2.imwrite(vidDir+str(i).zfill(4)+imgFormat,frames[:,:,i])
                        i += 1

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    screen_resolution = app.desktop().screenGeometry()
    form = Form(screen_resolution.width(),screen_resolution.height())
    screen = QtWidgets.QApplication.primaryScreen()
    sys.exit(app.exec_())