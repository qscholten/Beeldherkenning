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
camera.ExposureTime.Value = 20000
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

        # do some image processing
        #img = cv2.GaussianBlur(img, (65,65), 0)
        #img = cv2.GaussianBlur(img, (65,65), 0)
        
        kernel = numpy.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        #img = cv2.filter2D(img, -1,kernel)
        
        #img = cv2.Canny(img, 100, 200)
        
        # Histogram
        #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        histogram = cv2.calcHist(img, [0], None, [256], [0, 256])
        histogramimage = numpy.zeros((300, 512, 3), dtype=numpy.uint8)
        '''
        plt.figure()
        plt.title("Histogram")
        plt.xlabel("Bins")
        plt.ylabel("Percentage")
        plt.plot(histogram)
        plt.xlim(0, 256)
        plt.show()
        '''
        
        # open the image in a window
        imS = cv2.resize(img, ((int)(camera.Width.Value/6),
                               (int)(camera.Height.Value/6)))
        cv2.namedWindow('camera', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('camera', imS)

        # press esc (ascii 27) to exit
        k = cv2.waitKey(1)
        if k == 27:
            break
    grabResult.Release()

# Releasing the resource
camera.StopGrabbing()
cv2.destroyAllWindows()
