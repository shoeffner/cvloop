"""Provides ready to use example functions for the cvloop."""

import numpy as np
import cv2


class ForegroundExtractor:
    """Performs background subtraction using the supplied Subtractor and
    extracts the foreground accordingly."""

    def __init__(self, subtractor=None):
        """Initializes the ForegroundExtractor.

        Uses the BackgroundSubtractor supplied as subtractor to get a mask
        and apply the mask to the image.

        Args:
            subtractor: A BackgroundSubtractor. Defaults to an instance of
                        BackgroundSubtractorMOG2.
        """
        self.bg_sub = BackgroundSubtractorMOG2() if subtractor is None \
            else subtractor

    def __call__(self, image):
        """Returns the foreground of the image in colors. The background is
        black."""
        return image * (self.bg_sub(image) > 0)[:, :, np.newaxis]


class BackgroundSubtractorGMG:
    """Performs background subtraction with a mixture of gaussians.

    The method used was described by Godbehere, Matsukawa, and Goldberg in
    [Visual Tracking of Human Visitors under Variable-Lighting Conditions for a
    Responsive Audio Art Installation (2012)](
    http://goldberg.berkeley.edu/pubs/acc-2012-visual-tracking-final.pdf).

    See also
    http://docs.opencv.org/3.1.0/db/d5c/tutorial_py_bg_subtraction.html.
    """

    def __init__(self, structuring_element=None):
        """Initializes the BackgroundSubtractorGMG.

        Requires OpenCV to be built with --contrib as it uses the bgsegm
        package.

        Unless a custom structuring_element is specified, it uses:
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        """
        if structuring_element is None:
            self.strel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        else:
            self.strel = structuring_element
        self.fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()

    def __call__(self, image):
        """Returns a foreground mask of the image."""
        return cv2.morphologyEx(self.fgbg.apply(image), cv2.MORPH_OPEN,
                                self.strel)


class BackgroundSubtractorMOG:
    """Performs background subtraction with a mixture of gaussians.

    The method used was described by KaewTraKulPong and Bowden in
    [An improved adaptive background mixture model for real-time tracking with
    shadow detection (2001)](
    http://personal.ee.surrey.ac.uk/Personal/R.Bowden/publications/avbs01/avbs01.pdf).

    See also
    http://docs.opencv.org/3.1.0/db/d5c/tutorial_py_bg_subtraction.html.
    """

    def __init__(self):
        """Initializes the BackgroundSubtractorMOG.

        Requires OpenCV to be built with --contrib as it uses the bgsegm
        package.
        """
        self.fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

    def __call__(self, image):
        """Returns a foreground mask of the image."""
        return self.fgbg.apply(image)


class BackgroundSubtractorMOG2:
    """Performs background subtraction with a mixture of gaussians.

    The method used was described in two papers by Zivkovic and van der
    Heijden, [Improved adaptive Gausian mixture model for background
    subtraction (2004)](
    https://pdfs.semanticscholar.org/56b1/eee82a51ce17d72a91b5876a3281418679cc.pdf)
    and [Efficient Adaptive Density Estimation per Image Pixel for the
    Task of Background Subtraction (2006)](
    http://www.zoranz.net/Publications/zivkovicPRL2006.pdf)

    See also
    http://docs.opencv.org/3.1.0/db/d5c/tutorial_py_bg_subtraction.html.
    """
    def __init__(self):
        """Initializes the BackgroundSubtractorMOG2."""
        self.fgbg = cv2.createBackgroundSubtractorMOG2()

    def __call__(self, image):
        """Returns a foreground mask of the image."""
        return self.fgbg.apply(image)


class Inverter:
    """Inverts the colors of the image."""

    def __init__(self, high=255):
        """Initializes the inverter with a high value.

        Args:
            high: the value from which the image has to be subtracted.
                  Defaults to 255.
        """
        self.high = 255

    def __call__(self, image):
        """Calculates the image negative, i.e. self.high - image."""
        return 255 - image
