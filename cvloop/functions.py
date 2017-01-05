"""Provides ready to use example functions for the cvloop."""

import numpy as np
import cv2


def cv_foreground_extractor_gmg(image):
    """Performs background subtraction using the cv_background_subtractor_gmg and
    extracts the foreground accordingly.

    Args:
        image: The input image.
    Returns:
        The foreground of the image.
    """
    return image * (cv_background_subtractor_gmg(image) > 0)[:, :, np.newaxis]


def cv_foreground_extractor_mog(image):
    """Performs background subtraction using the cv_background_subtractor_mog and
    extracts the foreground accordingly.

    Args:
        image: The input image.
    Returns:
        The foreground of the image.
    """
    return image * (cv_background_subtractor_mog(image) > 0)[:, :, np.newaxis]


def cv_foreground_extractor_mog2(image):
    """Performs background subtraction using the cv_background_subtractor_mog2 and
    extracts the foreground accordingly.

    Args:
        image: The input image.
    Returns:
        The foreground of the image.
    """
    return image * (cv_background_subtractor_mog2(image) > 0)[:, :, np.newaxis]


def cv_background_subtractor_gmg(image):
    """Performs background subtraction with a mixture of gaussians.

    The method used was described by Godbehere, Matsukawa, and Goldberg in
    [Visual Tracking of Human Visitors under Variable-Lighting Conditions for a Responsive Audio Art Installation (2012)](http://goldberg.berkeley.edu/pubs/acc-2012-visual-tracking-final.pdf).

    See also http://docs.opencv.org/3.1.0/db/d5c/tutorial_py_bg_subtraction.html.

    Args:
        image: The input image.
    Returns:
        A mask for foreground extraction.
    """
    return cv2.morphologyEx(cv_background_subtractor_gmg.fgbg.apply(image),
                            cv2.MORPH_OPEN,
                            cv_background_subtractor_gmg.kernel)
cv_background_subtractor_gmg.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
cv_background_subtractor_gmg.fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()


def cv_background_subtractor_mog(image):
    """Performs background subtraction with a mixture of gaussians.

    The method used was described by KaewTraKulPong and Bowden in
    [An improved adaptive background mixture model for real-time tracking with shadow detection (2001)](http://personal.ee.surrey.ac.uk/Personal/R.Bowden/publications/avbs01/avbs01.pdf).

    See also http://docs.opencv.org/3.1.0/db/d5c/tutorial_py_bg_subtraction.html.

    Args:
        image: The input image.
    Returns:
        A mask for foreground extraction.
    """
    return cv_background_subtractor_mog.fgbg.apply(image)
cv_background_subtractor_mog.fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()


def cv_background_subtractor_mog2(image):
    """Performs background subtraction with a mixture of gaussians.

    The method used was described in two papers by Zivkovic and van der Heijden,
    [Improved adaptive Gausian mixture model for background subtraction (2004)](https://pdfs.semanticscholar.org/56b1/eee82a51ce17d72a91b5876a3281418679cc.pdf)
    and
    [Efficient Adaptive Density Estimation per Image Pixel for the Task of Background Subtraction (2006)](http://www.zoranz.net/Publications/zivkovicPRL2006.pdf)

    See also http://docs.opencv.org/3.1.0/db/d5c/tutorial_py_bg_subtraction.html.

    Args:
        image: The input image.
    Returns:
        A mask for foreground extraction.
    """
    return cv_background_subtractor_mog2.fgbg.apply(image)
cv_background_subtractor_mog2.fgbg = cv2.createBackgroundSubtractorMOG2()

def draw_hat(image,hatPath=None,wOffset=1.3,xOffset = -20,yOffset = 80):    
    wOffset = wOffset # Hat width additional scaling.
    xOffset = xOffset # Number of pixels right to move hat.
    yOffset = yOffset # Number of pixels down to move hat.    
    _hat = get_hat(hatPath)
    FRAME_HEIGHT = image.shape[0]
    FRAME_WIDTH = image.shape[1]
    hat = _hat.copy()
    faces = find_faces(image)
    
    
    origHatHeight = hat.shape[0]
    origHatWidth = hat.shape[1]
    hatWidth = hat.shape[1]
    for x,y,w,h in faces:
        # Scale hat to fit face.
        hatWidth = int(w * wOffset)
        hatHeight = int(hatWidth * origHatHeight / origHatWidth)
        hat = cv2.resize(hat, (hatWidth, hatHeight))

        # Clip hat if outside frame.
        hatLeft = hatTop = 0
        hatBottom = hatHeight
        hatRight = hatWidth        
        haty1 = hatHeight
        hatx1 = hatWidth        
        y0 = y - hatHeight + yOffset
        if y0 < 0: # If the hat starts above the frame, clip it.
            hatTop = abs(y0) # Find beginning of hat ROI.
            y0 = 0            
        y1 = y0 + hatHeight - hatTop        
        if y1 > FRAME_HEIGHT:
            hatBottom = hatHeight - (y1 - FRAME_HEIGHT)
            y1 = FRAME_HEIGHT            
        x0 = x + xOffset        
        if x0 < 0:
            hatLeft = abs(x0)
            x0 = 0            
        x1 = x0 + hatWidth - hatLeft        
        if x1 > FRAME_WIDTH:
            hatRight = hatWidth - (x1 - FRAME_WIDTH)
            x1 = FRAME_WIDTH
        
        # Remove background from hat image.
        for c in range(0, 3):        
            hatSlice = hat[hatTop:hatBottom, hatLeft:hatRight, c] * (hat[hatTop:hatBottom, hatLeft:hatRight, 3] / 255.0)
            backgroundSlice = image[y0:y1, x0:x1, c] * (1.0 - hat[hatTop:hatBottom, hatLeft:hatRight, 3] / 255.0)
            image[y0:y1, x0:x1, c] = hatSlice + backgroundSlice
        
    return image

def invert(image):
    """Inverts the colors of the image.

    Args:
        image: The input image.
    Returns:
        The inverted values (0 -> max, max -> 0).
    """
    return np.max(image) - image

def find_faces(image,cascPath='../examples/face.xml',drawBox=False):
    """Find faces.

    Args:
        image: The input image.

    Returns:
        Rectangle (x,y,w,h) with face position.
    """    
    faceCascade = cv2.CascadeClassifier(cascPath)
    frame_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale( \
        frame_gray, \
        scaleFactor=1.3, \
        minNeighbors=5, \
        minSize=(50, 50), \
        #         flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        flags=0)

    if drawBox:
        for x,y,w,h in faces:
            cv2.rectangle(image, (x, y),
                              (x + w, y + h), (0, 255, 0), 2)
    return faces

def get_hat(path=None):
    """Get `.png` hat image.
    """
    import random
    if path == None:
        hats = ['brownHat.png','xmasHat.png']
        path = '../examples/images/'
        randomHat = path + random.choice(hats)
        _hat = cv2.imread(randomHat,-1)
    else:
        _hat = cv2.imread(path,-1)
    b,g,r,a = cv2.split(_hat)
    _hat = cv2.merge((r,g,b,a))
    return _hat

