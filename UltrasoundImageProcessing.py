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
    def __init__(self):
        QtCore.QObject.__init__(self)
    
    @pyqtSlot(str,list,str,str)
    def digestVideos(self,filedir,vidFiles,vidFormat,imgFormat):
        nFiles = len(vidFiles)
        for fileNum,file in enumerate(vidFiles):
            print('Processing file ' + str(fileNum+1) + ' of ' + str(nFiles) + ': ' + file)
            cap = cv2.VideoCapture(filedir+file)
#                vidDir = self.dirField.text()+file.replace(vidFormat,'/')
#                if not os.path.isdir(vidDir):
#                    os.mkdir(vidDir)
            nFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.set(cv2.CAP_PROP_CONVERT_RGB,False)
            for i in range(nFrames):
                ret,frame = cap.read()
                cv2.imwrite(filedir+file.replace(vidFormat,'-' + str(i).zfill(4)+imgFormat),frame) if ret else None
                    

class myViewBox(QtWidgets.QWidget):
    def __init__(self,parent,wImage,hImage):
        super(myViewBox, self).__init__(parent)
        self.overlay = QtGui.QImage(wImage,hImage,QtGui.QImage.Format_RGBA8888)
        self.overlay.fill(QtGui.QColor("transparent"))
    
    def reset(self, image):
        self.overlay = image
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
            painter.setPen(self.pen)
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button == QtCore.Qt.LeftButton:
            self.drawing = False
        
class Form(QtWidgets.QMainWindow):
    requestDigestVideosSignal = pyqtSignal(str,list,str,str)
    def __init__(self,w,h):
        QtWidgets.QMainWindow.__init__(self)
        self.worker = Worker()
        self.thread = QThread()
        self.requestDigestVideosSignal.connect(self.worker.digestVideos)
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self.w = w
        self.h = h
        self.setupUi()
        
    def setupUi(self):
#        myFloatVal = QtGui.QRegExpValidator(QtCore.QRegExp('[\d]+[.]?[\d]*'))
        
        self.setObjectName('MainWindow')
        self.resize(self.w, self.h)
        self.showMaximized()
        self.setMaximumSize(QtCore.QSize(self.w, self.h))
        font = QtGui.QFont()
        font.setFamily('Segoe UI')
        font.setPointSize(10)
        self.setFont(font)
        self.setIconSize(QtCore.QSize(10, 10))
        self.setWindowTitle('Ultrasound Image Processor')
        
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
        self.groupBox.setGeometry(QtCore.QRect(int(0.005*self.w), int(0.01*self.h), int(0.15*self.w), int(0.9*self.h)))
        self.groupBox.setObjectName('groupBox')
        try:
            currentFile = os.path.realpath(__file__).replace('\\','/')
        except:
            currentFile = input('Python needs your help determining the location of this script.\nPlease copy the full filepath of this Python script from above,\nthen paste it here using right-click. Then press Enter to begin.\n')
        currentFile = currentFile.replace('\\','/')
        self.scriptdir = currentFile[:currentFile.rfind('/')+1]
        self.dirButton = QtWidgets.QPushButton(self.groupBox)
        self.dirButton.setGeometry(QtCore.QRect(int(0.005*self.w),int(0.01*self.h),int(0.015*self.w),int(0.025*self.h)))
        self.dirButton.setText('Dir')
        self.dirButton.setObjectName('dirButton')
        self.dirField = QtWidgets.QLineEdit(self.groupBox)
        self.dirField.setGeometry(QtCore.QRect(int(0.025*self.w), int(0.01*self.h), int(0.15*self.w-60), 25))
        self.dirField.setObjectName('dirField')
        self.dirField.setReadOnly(True)
        self.dirField.setText(self.scriptdir)
        self.leftButton = QtWidgets.QPushButton(self.groupBox)
        self.leftButton.setGeometry(QtCore.QRect(int(0.01*self.w),int(0.05*self.h),int(0.02*self.w),int(0.04*self.h)))
        self.leftButton.setText('<')
        self.leftButton.setObjectName('leftButton')
        self.rightButton = QtWidgets.QPushButton(self.groupBox)
        self.rightButton.setGeometry(QtCore.QRect(int(0.04*self.w),int(0.05*self.h),int(0.02*self.w),int(0.04*self.h)))
        self.rightButton.setText('>')
        self.rightButton.setObjectName('rightButton')
        self.saveButton = QtWidgets.QPushButton(self.groupBox)
        self.saveButton.setGeometry(QtCore.QRect(int(0.07*self.w),int(0.05*self.h),int(0.03*self.w),int(0.04*self.h)))
        self.saveButton.setText('Save')
        self.saveButton.setObjectName('saveButton')
        self.clearButton = QtWidgets.QPushButton(self.groupBox)
        self.clearButton.setGeometry(QtCore.QRect(int(0.11*self.w),int(0.05*self.h),int(0.03*self.w),int(0.04*self.h)))
        self.clearButton.setText('Clear')
        self.clearButton.setObjectName('clearButton')
        self.processButton = QtWidgets.QPushButton(self.groupBox)
        self.processButton.setGeometry(QtCore.QRect(int(0.035*self.w),int(0.1*self.h),int(0.08*self.w),int(0.04*self.h)))
        self.processButton.setText('Process Stored Images')
        self.processButton.setObjectName('processButton')
        self.digestVideosButton = QtWidgets.QPushButton(self.groupBox)
        self.digestVideosButton.setGeometry(QtCore.QRect(int(0.05*self.w),int(0.15*self.h),int(0.05*self.w),int(0.04*self.h)))
        self.digestVideosButton.setText('Digest Videos')
        self.digestVideosButton.setObjectName('digestVideosButton')
        self.imgFormatLabel = QtWidgets.QLineEdit(self.groupBox)
        self.imgFormatLabel.setGeometry(QtCore.QRect(int(0.025*self.w),int(0.2*self.h),int(0.05*self.w),int(0.04*self.h)))
        self.imgFormatLabel.setText('Image Format')
        self.imgFormatLabel.setObjectName('imgFormatLabel')
        self.imgFormatLabel.setReadOnly(True)
        self.vidFormatLabel = QtWidgets.QLineEdit(self.groupBox)
        self.vidFormatLabel.setGeometry(QtCore.QRect(int(0.085*self.w),int(0.2*self.h),int(0.05*self.w),int(0.04*self.h)))
        self.vidFormatLabel.setText('Video Format')
        self.vidFormatLabel.setObjectName('vidFormatLabel')
        self.vidFormatLabel.setReadOnly(True)
        self.imgFormatDropDown = QtWidgets.QComboBox(self.groupBox)
        self.imgFormatDropDown.setGeometry(QtCore.QRect(int(0.025*self.w),int(0.25*self.h),int(0.05*self.w),int(0.04*self.h)))
        self.imgFormatDropDown.addItems(['.tif','.jpg','.png'])
        self.imgFormatDropDown.setObjectName('imgFormatDropDown')
        self.vidFormatDropDown = QtWidgets.QComboBox(self.groupBox)
        self.vidFormatDropDown.setGeometry(QtCore.QRect(int(0.085*self.w),int(0.25*self.h),int(0.05*self.w),int(0.04*self.h)))
        self.vidFormatDropDown.addItems(['.m4v','.avi','.mov','.mp4'])
        self.vidFormatDropDown.setObjectName('vidFormatDropDown')
        self.redButton = QtWidgets.QPushButton(self.groupBox)
        self.redButton.setGeometry(QtCore.QRect(int(0.04*self.w),int(0.3*self.h),int(0.03*self.w),int(0.04*self.h)))
        self.redButton.setText('Red')
        self.redButton.setObjectName('redButton')
        self.blueButton = QtWidgets.QPushButton(self.groupBox)
        self.blueButton.setGeometry(QtCore.QRect(int(0.075*self.w),int(0.3*self.h),int(0.03*self.w),int(0.04*self.h)))
        self.blueButton.setText('Blue')
        self.blueButton.setObjectName('blueButton')
        self.greenButton = QtWidgets.QPushButton(self.groupBox)
        self.greenButton.setGeometry(QtCore.QRect(int(0.11*self.w),int(0.3*self.h),int(0.03*self.w),int(0.04*self.h)))
        self.greenButton.setText('Green')
        self.greenButton.setObjectName('greenButton')
        
        saveAction = QtWidgets.QAction('Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveImage)
        self.addAction(saveAction)
        
        prevImage = QtWidgets.QAction('PrevTab', self)
        prevImage.setShortcut('F')
        prevImage.triggered.connect(self.prevImage)
        self.addAction(prevImage)
        
        nextImage = QtWidgets.QAction('NextTab', self)
        nextImage.setShortcut('G')
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
        self.imgFormatDropDown.currentIndexChanged.connect(self.loadImageList)
        self.vidFormatDropDown.currentIndexChanged.connect(self.loadVideoList)
        self.redButton.clicked.connect(self.redButtonPressed)
        self.greenButton.clicked.connect(self.greenButtonPressed)
        self.blueButton.clicked.connect(self.blueButtonPressed)
        
        self.loadImageList()
        self.loadVideoList()
        self.show()
        
        
    def loadImageList(self):
        filesAndFolders = os.listdir(self.dirField.text())
        self.imgFiles = [fileOrFolder for fileOrFolder in filesAndFolders if self.imgFormatDropDown.currentText() in fileOrFolder and '-mask' not in fileOrFolder]
        self.imgIndex = 0
        self.prevIndex = 0
        if len(self.imgFiles) > 0:
            self.image = QtGui.QImage(self.dirField.text() + self.imgFiles[self.imgIndex])
            wImage,hImage = self.image.width(), self.image.height()
            self.overlay = QtGui.QImage(wImage,hImage,QtGui.QImage.Format_RGBA8888)
            self.overlay.fill(QtGui.QColor("transparent"))
            self.changeImage()
        
    def loadVideoList(self):
        filesAndFolders = os.listdir(self.dirField.text())
        self.vidFiles = [fileOrFolder for fileOrFolder in filesAndFolders if self.vidFormatDropDown.currentText() in fileOrFolder]
        
    def changeImage(self):
        if len(self.imgFiles) > 0:
            self.image = QtGui.QImage(self.dirField.text() + self.imgFiles[self.imgIndex])
            wImage,hImage = self.image.width(), self.image.height()
            if len(self.centralwidget.children()) > 1:
                self.backgroundBox.deleteLater()
                self.vL.deleteLater()
            self.backgroundBox = QtWidgets.QLabel(self.centralwidget)
            self.backgroundBox.setGeometry(QtCore.QRect(int(0.5*self.w-0.5*wImage), int(0.5*self.h-0.5*hImage), wImage,hImage))
            self.backgroundBox.setPixmap(QtGui.QPixmap(self.image))
            self.backgroundBox.setObjectName('backgroundBox')
            self.backgroundBox.show()
            self.vL = myViewBox(self.centralwidget,wImage,hImage)
            self.vL.setGeometry(QtCore.QRect(int(0.5*self.w-0.5*wImage), int(0.5*self.h-0.5*hImage), wImage,hImage))
            self.vL.setObjectName('vL')
            self.vL.pen = QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.SolidLine)
            self.vL.reset(self.overlay)
            self.vL.show()
            
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
            self.changeImage()
    
    def clearDrawing(self):
        if len(self.imgFiles) > 0:
            wImage,hImage = self.image.width(), self.image.height()
            self.overlay = QtGui.QImage(wImage,hImage,QtGui.QImage.Format_RGBA8888)
            self.overlay.fill(QtGui.QColor("transparent"))
            self.vL.reset(self.overlay)
            self.vL.setGeometry(QtCore.QRect(int(0.5*self.w-0.5*wImage), int(0.5*self.h-0.5*hImage), wImage,hImage))
        
        
    def prevImage(self):
        if self.imgIndex > 0:
            self.prevIndex = self.imgIndex
            self.imgIndex -= 1
        else:
            self.prevIndex = 0
            self.imgIndex = len(self.imgFiles) - 1
        self.changeImage()
    
    def nextImage(self):
        if len(self.imgFiles) > self.imgIndex + 1:
            self.prevIndex = self.imgIndex
            self.imgIndex += 1
        else:
            self.prevIndex = len(self.imgFiles) - 1
            self.imgIndex = 0
        self.changeImage()
    
    def saveImage(self):
        if len(self.imgFiles) > 0:
            p = self.vL.grab()
            q = QtGui.QImage(p)
            sz = q.size()
            buffer = q.bits()
            w,h = sz.width(),sz.height()
            buffer.setsize(w*h*q.depth())
            arr = np.ndarray(shape  = (sz.height(), sz.width(), q.depth()//8),
                     buffer = buffer,
                     dtype  = np.uint8)
            if w != self.image.width() or h!= self.image.height():
                arr4 = cv2.resize(arr,(self.image.width(),self.image.height()))
            else:
                arr4 = arr.copy()
            mask3d = arr4[:,:,0:3] > 200
            arr4[:,:,3] = (255*np.any(mask3d,axis=2)).astype(np.uint8)
            arr3 = arr4.copy()
            arr3[:,:,0] = arr4[:,:,2]
            arr3[:,:,2] = arr4[:,:,0]
            self.overlay = QtGui.QImage(arr3,w,h,4*w,QtGui.QImage.Format_RGBA8888)
            f = self.imgFormatDropDown.currentText()
            self.overlay.save(self.dirField.text()+self.imgFiles[self.imgIndex].replace(f,'-mask' + f), f.replace('.',''))
            self.nextImage()
    
    def processImages(self):
        if len(self.imgFiles) > 0:
            redAnswerz = ['Error applying mask']*len(self.imgFiles)
            greenAnswerz = ['Error applying mask']*len(self.imgFiles)
            blueAnswerz = ['Error applying mask']*len(self.imgFiles)
            imgFormat = self.imgFormatDropDown.currentText()
            for z,file in enumerate(self.imgFiles):
                if os.path.isfile(self.dirField.text()+file.replace(imgFormat,'-mask' + imgFormat)):
                    maskAllChannels = cv2.imread(self.dirField.text()+file.replace(imgFormat,'-mask'+ imgFormat))
                    hMask, wMask = np.shape(maskAllChannels)[0],np.shape(maskAllChannels)[1]
                    maskFound = True
                    break
                else:
                    maskFound = False
            if not maskFound:
                redAnswerz = ['Mask file not found.']*len(self.imgFiles)
                greenAnswerz = ['Mask file not found.']*len(self.imgFiles)
                blueAnswerz = ['Mask file not found.']*len(self.imgFiles)
            else:
                for z,file in enumerate(self.imgFiles):
                    img = cv2.imread(self.dirField.text()+file)[:,:,0]
                    hImg,wImg = np.shape(img)
                    if hImg == hMask and wImg == wMask:
                        colorMask = maskAllChannels < 10
                        redRegion,nRed = nd.label(colorMask[:,:,2])
                        greenRegion,nGreen = nd.label(colorMask[:,:,1])
                        blueRegion,nBlue = nd.label(colorMask[:,:,0])
                        if nRed > 1:
                            c = np.zeros(nRed,np.uint32)
                            for i in range(nRed):
                                c[i] = np.count_nonzero(redRegion==i+1)
                            redMaskedImg = np.ma.array(img,mask=redRegion!=(np.argmin(c)+1))
                            redAnswerz[z] = redMaskedImg.mean()
                        if nGreen > 1:
                            d = np.zeros(nGreen,np.uint32)
                            for i in range(nGreen):
                                d[i] = np.count_nonzero(greenRegion==i+1)
                            greenMaskedImg = np.ma.array(img,mask=greenRegion!=(np.argmin(d)+1))
                            greenAnswerz[z] = greenMaskedImg.mean()
                        if nBlue  > 1:
                            e = np.zeros(nBlue,np.uint32)
                            for i in range(nBlue):
                                e[i] = np.count_nonzero(blueRegion==i+1)
                            blueMaskedImg = np.ma.array(img,mask=blueRegion!=(np.argmin(e)+1))
                            blueAnswerz[z] = blueMaskedImg.mean()
                    else:
                        redAnswerz[z] = ['Mask and image size don\'t match']
                        greenAnswerz[z] = ['Mask and image size don\'t match']
                        blueAnswerz[z] = ['Mask and image size don\'t match']
                
            excelFileName = self.dirField.text() + 'Image Processing Output - 1.xlsx'
            a = 1
            while os.path.isfile(excelFileName):
                a += 1
                excelFileName = excelFileName.replace('Output - ' + str(a-1) + '.xlsx','Output - '+str(a) + '.xlsx')
            writer = pd.ExcelWriter(excelFileName)
            df = pd.DataFrame(self.imgFiles)
            df.to_excel(writer, startrow=0, startcol = 0, sheet_name='Image Processing', header = ['Filename'], index=False, engine='xlsxwriter')
            df2 = pd.DataFrame(redAnswerz)
            df2.to_excel(writer, startrow=0, startcol = 1, sheet_name='Image Processing', header = ['Average Brightness 1 [Red]'], index=False, engine='xlsxwriter')
            df2 = pd.DataFrame(greenAnswerz)
            df2.to_excel(writer, startrow=0, startcol = 2, sheet_name='Image Processing', header = ['Average Brightness 2 [Green]'], index=False, engine='xlsxwriter')
            df2 = pd.DataFrame(blueAnswerz)
            df2.to_excel(writer, startrow=0, startcol = 3, sheet_name='Image Processing', header = ['Average Brightness 3 [Blue]'], index=False, engine='xlsxwriter')
            writer.sheets['Image Processing'].set_column('A:A',50,None)
            writer.sheets['Image Processing'].set_column('B:B',40,None)
            writer.sheets['Image Processing'].set_column('C:C',40,None)
            writer.sheets['Image Processing'].set_column('D:D',40,None)
            writer.save()
        
    def digestVideos(self):
        nFiles = len(self.vidFiles)
        if nFiles > 0:
            self.requestDigestVideosSignal.emit(self.dirField.text(),self.vidFiles,self.vidFormatDropDown.currentText(),self.imgFormatDropDown.currentText())
            
    def redButtonPressed(self):
        try:
            self.vL
            self.vL.pen = QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.SolidLine)
        except:
            None
        
        
    def greenButtonPressed(self):
        try:
            self.vL
            self.vL.pen = QtGui.QPen(QtCore.Qt.green, 2, QtCore.Qt.SolidLine)
        except:
            None
        
    def blueButtonPressed(self):
        try:
            self.vL
            self.vL.pen = QtGui.QPen(QtCore.Qt.blue, 2, QtCore.Qt.SolidLine)
        except:
            None
            

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    screen_resolution = app.desktop().screenGeometry()
    form = Form(screen_resolution.width(),screen_resolution.height())
    screen = app.primaryScreen()
    sys.exit(app.exec_())