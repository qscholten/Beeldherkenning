'''
A simple Program for grabbing video from basler camera and converting it to opencv img.
Uitleg Gert: 
Gebruik de Pylon Viewer om namen van parameters op te zoeken.
Voor python is er geen directe API. Hier staan de sources: https://github.com/basler/pypylon
Zorg dat je in Baslerweb deze camera ingesteld hebt: https://docs.baslerweb.com/pua2500-14uc
Dan kun je een poging doen om te zoeken in de C++ API: https://docs.baslerweb.com/pylonapi/

'''

from pypylon import pylon
import cv2
import time
import numpy
from matplotlib import pyplot as plt

# Print version string
print ("OpenCV version :  {0}".format(cv2.__version__))

# connecting to the first available camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

#set the dimensions of the image to grab
camera.Open()
camera.Width.Value = 2592  # max width of Basler puA2500-14uc camera
camera.Height.Value = 1944 # max height of Basler puA2500-14uc camera

# camera.OffsetX.Value = 518
camera.AcquisitionFrameRate.SetValue(10) # 10 beelden per seconde

# set features of camera
camera.ExposureTime.Value = 200000#20000
camera.ExposureAuto.SetValue('Off')
camera.BalanceWhiteAuto.SetValue('Off')
camera.LightSourcePreset.SetValue('Off')
camera.GainAuto.SetValue('Off')
camera.GainRaw.Value = 48
#pylon.FeaturePersistence.Save("test.txt", camera.GetNodeMap())

print("Using device: ", camera.GetDeviceInfo().GetModelName())
print("width set: ",camera.Width.Value)
print("Height set: ",camera.Height.Value)

# The parameter MaxNumBuffer can be used to control the count of buffers
# allocated for grabbing. The default value of this parameter is 10.
camera.MaxNumBuffer = 5

# Grabing Continusely (video) with minimal delay
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()

# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Access the image data
        image = converter.Convert(grabResult)
        img = image.GetArray()
        imgorigineel = img
        imorgineel = cv2.resize(imgorigineel, ((int)(camera.Width.Value/6),
                               (int)(camera.Height.Value/6)))
        cv2.namedWindow('Orgineel', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Orgineel', imorgineel)

        # do some image processing
        
        
        
        # ENHANCEMENT           
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Histogram
        #histogram = cv2.calcHist(img, [0], None, [256], [0, 256])
        #cv2.normalize(histogram,histogram, 0,255,cv2.NORM_MINMAX)
        
        h = numpy.zeros((300, 256, 3))
        bins = numpy.arange(256).reshape(256, 1)
        color = [ (255, 255, 255)]
        for ch, col in enumerate(color):
            hist_item = cv2.calcHist(img, [ch], None, [256], [0, 255])
            cv2.normalize(hist_item, hist_item, 0, 255, cv2.NORM_MINMAX)
            hist = numpy.int32(numpy.around(hist_item))
            pts = numpy.column_stack((bins, hist))
            cv2.polylines(h, [pts], False, col)
        h = numpy.flipud(h)
        cv2.imshow('Histogram', h)
        
        img = cv2.GaussianBlur(img, (65,65), 0)
        img = cv2.GaussianBlur(img, (65,65), 0)
        #img = cv2.GaussianBlur(img, (65,65), 0)
        
        #img = cv2.Canny(img, 100, 200)
        
        imS = cv2.resize(img, ((int)(camera.Width.Value/6),
                               (int)(camera.Height.Value/6)))
        cv2.namedWindow('Enhancement', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Enhancement', imS)
        
        kernel = numpy.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        #img = cv2.filter2D(img, -1,kernel)
        #img = cv2.Canny(img, 100, 200)
        #img = cv2.equalizeHist(img)
        
        # SEGMENTATION
        ret3,th3 = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        imSth3 = cv2.resize(th3, ((int)(camera.Width.Value/6),
                               (int)(camera.Height.Value/6)))
        cv2.namedWindow('Threshold', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Threshold', imSth3)
        
        '''
        kernel = numpy.ones((10,10),numpy.uint8)
        opening = cv2.morphologyEx(th3, cv2.MORPH_OPEN, kernel)
        #closing = cv2.morphologyEx(th3, cv2.MORPH_CLOSE, kernel)
        imSth5 = cv2.resize(opening, ((int)(camera.Width.Value/6),
                               (int)(camera.Height.Value/6)))
        cv2.namedWindow('Opening', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Opening', imSth5)
        '''
        
        '''
        kernel = numpy.ones((5,5),numpy.uint8)
        DifDilEr = cv2.morphologyEx(opening, cv2.MORPH_GRADIENT, kernel)
        imSth4 = cv2.resize(DifDilEr, ((int)(camera.Width.Value/6),
                               (int)(camera.Height.Value/6)))
        cv2.namedWindow('Dilation-Erosion', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Dilation-Erosion', imSth4)
        '''
    
        # press esc (ascii 27) to exit
        k = cv2.waitKey(1)
        if k == 27:
            break
    grabResult.Release()

# Releasing the resource
camera.StopGrabbing()
cv2.destroyAllWindows()
