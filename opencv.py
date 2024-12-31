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
        imgorigineel = cv2.resize(imgorigineel, ((int)(camera.Width.Value/6),
                               (int)(camera.Height.Value/6)))
        '''
        cv2.namedWindow('Orgineel', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Orgineel', imorgineel)
        '''
        
        # Histogram
        #histogram = cv2.calcHist(img, [0], None, [256], [0, 256])
        #cv2.normalize(histogram,histogram, 0,255,cv2.NORM_MINMAX)
        
        '''
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
        '''
        
        # ENHANCEMENT           
        img = cv2.cvtColor(imgorigineel, cv2.COLOR_BGR2GRAY)
        img = cv2.GaussianBlur(img, (11,11), 0)
        '''
        cv2.namedWindow('Enhancement', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Enhancement', img)
        '''
        
        # SEGMENTATION
        ret3,th3 = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        
        cv2.namedWindow('Threshold', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Threshold', th3)
        

        # FEATURE EXTRACTION
        contours, hierarchy = cv2.findContours(image=th3, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        imagecontours = imgorigineel.copy()
        cv2.drawContours(image=imagecontours, contours=contours, contourIdx=-1, color=(0, 0, 255), thickness=1, lineType=cv2.LINE_AA)
        
        cv2.namedWindow('Contours', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Contours', imagecontours)
        
        
        # RING TEMPLATE
        ring = cv2.imread('ring.png', cv2.IMREAD_COLOR)
        ringgray = cv2.cvtColor(ring, cv2.COLOR_BGR2GRAY)
        ringgaus = cv2.GaussianBlur(ringgray, (11,11), 0)
        ret3ring,th3ring = cv2.threshold(ringgaus,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        contoursring, hierarchyring = cv2.findContours(image=th3ring, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(image=ring, contours=contoursring, contourIdx=-1, color=(0, 0, 255), thickness=1, lineType=cv2.LINE_AA)
        cv2.namedWindow('Ring', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Ring', ring)
        
        # MOER TEMPLATE
        moer = cv2.imread('moer.png', cv2.IMREAD_COLOR)
        moergray = cv2.cvtColor(moer, cv2.COLOR_BGR2GRAY)
        moergaus = cv2.GaussianBlur(moergray, (11,11), 0)
        ret3moer, th3moer = cv2.threshold(moergaus, 0, 255, cv2.THREAS_BINARY+cv2.THRESH_OTSU)
        contoursmoer, hierarchymoer = cv2.findContours(image=th3moer, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(image=moer, contours=contoursring, contourIdx=-1, color=(0, 0, 255), thickness=1, lineType=cv2.LINE_AA)
        cv2.namedWindow('Moer', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Moer', moer)
        
        # SCHROEF TEMPLATE
        schroef = cv2.imread('schroef.png', cv2.IMREAD_COLOR)
        schroefgray = cv2.cvtColor(schroef, cv2.COLOR_BGR2GRAY)
        schroefgaus = cv2.GaussianBlur(schroefgray, (11,11), 0)
        ret3schroef, th3schroef = cv2.threshold(schroefgaus, 0, 255, cv2.THREAS_BINARY+cv2.THRESH_OTSU)
        contoursschroef, hierarchyschroef = cv2.findContours(image=th3schroef, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(image=schroef, contours=contoursring, contourIdx=-1, color=(0, 0, 255), thickness=1, lineType=cv2.LINE_AA)
        cv2.namedWindow('Schroef', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Schroef', schroef)
        
        # SPIJKER TEMPLATE
        spijker = cv2.imread('spijker.png', cv2.IMREAD_COLOR)
        spijkergray = cv2.cvtColor(spijker, cv2.COLOR_BGR2GRAY)
        spijkergaus = cv2.GaussianBlur(spijkergray, (11,11), 0)
        ret3spijker, th3spijker = cv2.threshold(spijkergaus, 0, 255, cv2.THREAS_BINARY+cv2.THRESH_OTSU)
        contoursspijker, hierarchyspijker = cv2.findContours(image=th3spijker, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(image=spijker, contours=contoursring, contourIdx=-1, color=(0, 0, 255), thickness=1, lineType=cv2.LINE_AA)
        cv2.namedWindow('Spijker', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Spijker', spijker)
        
        for c in contours: 
            match = cv2.matchShapes(contoursring[1], c, 1, 0.0)
            if match < 0.15:
                closest_contour = c
            else:
                closest_contour = []
        imgmatch = imgorigineel.copy()
        print(contours[0])
        # if contours.size
        cv2.drawContours(imgmatch, [closest_contour], -1, (0, 255, 0), 3)
        cv2.imshow("Output", imgmatch)
        
        # press esc (ascii 27) to exit
        k = cv2.waitKey(1)
        if k == 27:
            break
    grabResult.Release()

# Releasing the resource
camera.StopGrabbing()
cv2.destroyAllWindows()
