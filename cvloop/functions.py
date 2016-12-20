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


def invert(image):
    """Inverts the colors of the image.

    Args:
        image: The input image.
    Returns:
        The inverted values (0 -> max, max -> 0).
    """
    return np.max(image) - image

