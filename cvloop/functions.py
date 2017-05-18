"""Provides ready to use example functions for the cvloop."""

from . import OPENCV_CASCADE_PATH
import os
import numpy as np
import cv2


class ForegroundExtractor:
    """Performs background subtraction using the supplied Subtractor and
    extracts the foreground accordingly."""

    def __init__(self, subtractor=None):
        """Initializes the `ForegroundExtractor`.

        Uses the supplied BackgroundSubtractor as subtractor to get a mask
        and apply the mask to the image.

        Args:
            subtractor: A BackgroundSubtractor. Defaults to an instance of
                        `BackgroundSubtractorMOG2`.
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
        """Initializes the `BackgroundSubtractorGMG`.

        *Note:* Requires OpenCV to be built with `--contrib` as it uses the
        `bgsegm` package.

        Unless a custom `structuring_element` is specified, it uses:
            `cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))`

        Args:
            structuring_element: The structuring element.
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
        """Initializes the `BackgroundSubtractorMOG`.

        *Note:* Requires OpenCV to be built with `--contrib` as it uses the
        `bgsegm` package.
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
        """Initializes the `BackgroundSubtractorMOG2`."""
        self.fgbg = cv2.createBackgroundSubtractorMOG2()

    def __call__(self, image):
        """Returns a foreground mask of the image."""
        return self.fgbg.apply(image)


class Inverter:
    """Inverts the colors of the image."""

    def __init__(self, high=255):
        """Initializes the `Inverter` with a high value.

        Args:
            high: the value from which the image has to be subtracted.
                  Defaults to 255.
        """
        self.high = 255

    def __call__(self, image):
        """Calculates the image negative, i.e. self.high - image."""
        return 255 - image


class DrawHat:
    """Draws hats above detected faces.

    Uses a Haar cascade for face detection and draws provided hats above the
    detected faces.

    The default hat (examples/hat.png) is taken from
    https://pixabay.com/en/hat-trilby-black-brim-crease-felt-157581/
    and was released unter CC0 Public Domain.
    """

    def __init__(self, hat_path=os.path.join(os.curdir, 'hat.png'),
                 cascade_path=os.path.join(
                              OPENCV_CASCADE_PATH, 'haarcascades',
                              'haarcascade_frontalface_default.xml'),
                 w_offset=1.3, x_offset=-20, y_offset=80, draw_box=False):
        """Initializes a `DrawHat` instance.

        Args:
            hat_path: The path to the hat file. Defaults to ./hat.png .
            cascade_path: The path to the face cascade file.
                          Defaults to cvloop.OPENCV_CASCADE_PATH/haarcascades/
                                        haarcascade_frontalface_default.xml
            w_offset: Hat width additional scaling.
            x_offset: Number of pixels right to move hat.
            y_offset: Number of pixels down to move hat.
            draw_box: If True, draws boxes around detected faces.
        """
        self.w_offset = w_offset
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.draw_box = draw_box

        self.cascade = cv2.CascadeClassifier(cascade_path)
        self.hat = self.load_hat(hat_path)

    def load_hat(self, path):
        hat = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if hat is None:
            raise ValueError('No hat image found at `{}`'.format(path))
        b, g, r, a = cv2.split(hat)
        return cv2.merge((r, g, b, a))

    def find_faces(self, image, draw_box=False):
        frame_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        faces = self.cascade.detectMultiScale(
                frame_gray,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(50, 50),
                flags=0)

        if draw_box:
            for x, y, w, h in faces:
                cv2.rectangle(image, (x, y),
                              (x + w, y + h), (0, 255, 0), 2)
        return faces

    def __call__(self, image):
        frame_height = image.shape[0]
        frame_width = image.shape[1]

        faces = self.find_faces(image, self.draw_box)

        for x, y, w, h in faces:
            hat = self.hat.copy()

            # Scale hat to fit face.
            hat_width = int(w * self.w_offset)
            hat_height = int(hat_width * hat.shape[0] / hat.shape[1])
            hat = cv2.resize(hat, (hat_width, hat_height))

            # Clip hat if outside frame.
            hat_left = 0
            hat_top = 0
            hat_bottom = hat_height
            hat_right = hat_width
            y0 = y - hat_height + self.y_offset
            if y0 < 0:  # If the hat starts above the frame, clip it.
                hat_top = abs(y0)  # Find beginning of hat ROI.
                y0 = 0
            y1 = y0 + hat_height - hat_top
            if y1 > frame_height:
                hat_bottom = hat_height - (y1 - frame_height)
                y1 = frame_height
            x0 = x + self.x_offset
            if x0 < 0:
                hat_left = abs(x0)
                x0 = 0
            x1 = x0 + hat_width - hat_left
            if x1 > frame_width:
                hat_right = hat_width - (x1 - frame_width)
                x1 = frame_width

            # Remove background from hat image.
            for c in range(0, 3):
                hat_slice = hat[hat_top:hat_bottom, hat_left:hat_right, c] * \
                    (hat[hat_top:hat_bottom, hat_left:hat_right, 3] / 255.0)
                bg_slice = image[y0:y1, x0:x1, c] * \
                    (1.0 - hat[hat_top:hat_bottom, hat_left:hat_right, 3]
                     / 255.0)
                image[y0:y1, x0:x1, c] = hat_slice + bg_slice

        return image
