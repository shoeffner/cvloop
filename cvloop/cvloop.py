"""Provides a videoloop to be used in jupyter notebooks.

Please use the proper backend by using
%matplotlib notebook
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt


def cvloop(source=0, function=lambda x: x,
           side_by_side=False, convert_color=cv2.COLOR_BGR2RGB,
           cmaps=None):
    """Runs a video loop for the specified source and modifies the stream with the function.

    The source can either be an integer for a webcam device, a string to load a video file or
    a VideoCapture object. In the last case, the capture object will not be released by this
    function.

    The function takes in a frame and returns the modified frame. The default value just passes
    the value through, it is equivalent to the identity function.

    If side_by_side is True, the input as well as the modified image are shown side by side,
    otherwise only the output is shown.

    If convert_color can be any value for cv2.cvtColor, e.g. cv2.COLOR_BGR2RGB. If it is -1, no
    color conversion is performed, otherwise a color conversion using cv2.cvtColor is performed
    before the image is passed to the function.

    Args:
        source:        The video source; ints for webcams/devices, a string to load a video file.
                       To fine tune a video source, it is possible to pass a VideoCapture object
                       directly. If that is the case, this function does not attempt
                       to release the object.
                       (Default: 0)
        function:      The modification function.
                       (Default: identity function lambda x: x)
        side_by_side:  If True, both images are shown, the original and the modified image.
                       (Default: False)
        convert_color: Converts the image with the given value using cv2.cvtColor, unless
                       value is -1.
                       (Default: cv2.COLOR_BGR2RGB)
        cmaps:         If None, the plot function makes guesses about what
                       color maps to use (if at all). If a single value,
                       that color map is used for all plots (e.g. cmaps='gray').
                       If cmaps is a tuple, the first value is used on the
                       original image, the second value for the modified image.
                       If cmaps is a tuple, None-entries are ignored and result
                       in the normal guessing.
    Returns:
        The capture object. In case it is not properly released or it was passed in from the
        outside, it can be released using
        capture.release()
    """
    # Select source
    source_is_capture = isinstance(source, type(cv2.VideoCapture())) or hasattr(source, 'read')
    capture = source if source_is_capture else cv2.VideoCapture(source)

    # Prepare plotting and select plot function
    plot = VideoPlot(capture, side_by_side, cmaps)
    try:
        # until interrupted or finished
        while True:
            # Read frame from camera
            ret, frame = capture.read()

            # If video is empty / device did not return a frame: release and abort
            if not ret:
                if not source_is_capture:
                    capture.release()
                print("Finished video processing.")
                break

            # If the image has to be color converted, perform the conversion
            if convert_color != -1 and is_color_image(frame):
                frame = cv2.cvtColor(frame, convert_color)

            # apply the passed function
            modified = function(frame)

            # plot with the selected plotfunction
            plot(frame, modified)

            # clean up memory
            frame, modified = None, None
    except KeyboardInterrupt:
        # Release video stream on keyboard interrupt
        if not source_is_capture:
            capture.release()
        print("Interrupting video processing.")
    return capture


class VideoPlot:
    """Provides a class to plot video stream data, either as single plots or side by side with
    modifications."""

    figurecounter = 0

    def __init__(self, capture, side_by_side=False, cmaps=None):
        """Initializes the VideoPlot.

        Args:
            capture:      A cv2.VideoCapture object.
            side_by_side: True to plot original and modified video.
            cmaps:        If None, the plot function makes guesses about what
                          color maps to use (if at all). If a single value,
                          that color map is used for all plots (e.g. cmaps='gray').
                          If cmaps is a tuple, the first value is used on the
                          original image, the second value for the modified image.
                          If cmaps is a tuple, None-entries are ignored and result
                          in the normal guessing.
        """
        self.side_by_side = side_by_side
        self.capture = capture
        self.figure_title = self.__prepare_plot(capture)
        self.cmaps = cmaps


    def __call__(self, frame, modified=None):
        """Plots the video stream.

        If side_by_side is true, the original and the modified
        image are plotted.
        """
        if self.side_by_side:
            self.__plot_side_by_side(frame, modified)
        else:
            self.__imshow(modified, 0)
        plt.figure(self.figure_title).canvas.draw()


    def __prepare_plot(self, capture=None):
        """Prepares the figure to plot the video stream into.

        Args:
            capture: the capture source to read out FPS and resolution.
        Returns:
            The prepared figure's title.
        """
        VideoPlot.figurecounter += 1

        # prepare figure title
        title = 'Video Stream'
        if capture and hasattr(capture, 'get'):
            width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = capture.get(cv2.CAP_PROP_FPS)
            title += ' {}x{} @ {} FPS'.format(width, height, fps)
        title += ' (Fig. {})'.format(VideoPlot.figurecounter)
        plt.figure(title)

        # prepare figure area
        if self.side_by_side:
            plt.subplot(1, 2, 1)
            plt.title('Original')
            plt.axis('off')
            plt.subplot(1, 2, 2)
            plt.title('Processed')
            plt.axis('off')
        else:
            plt.title('Processed')
            plt.axis('off')

        return title


    def __plot_side_by_side(self, left, right):
        """Plots the left and right image next to each other.

        Args:
            left:  The image to plot on the left.
            right: The image to plot on the right.
        """
        plt.subplot(1, 2, 1)
        self.__imshow(left, 0)
        plt.subplot(1, 2, 2)
        self.__imshow(right, 1)


    def __imshow(self, frame, cmap_idx=0):
        """Makes some guesses about how to plot a frame.

        If only one color channel is present, it uses the
        colormap 'gray'.
        Otherwise the full color image will be shown.

        Args:
            frame:    The frame to show.
            cmap_idx: Index to select cmap from self.cmaps.
        """
        if self.cmaps:
            if isinstance(self.cmaps, str):
                plt.imshow(to_gray(frame), cmap=self.cmaps)
                return
            try:
                if self.cmaps[cmap_idx]:
                    plt.imshow(to_gray(frame), cmap=self.cmaps[cmap_idx])
                    return
            except IndexError:
                pass

        if len(frame.shape) > 2:
            plt.imshow(frame)
        else:
            plt.imshow(frame, cmap='gray')


def is_color_image(image):
    """Tests if the image is a color image.

    Args:
       image: the input image to check.
    Returns:
        True if the image has at least three dimensions and the last dimension is at least 3."""
    return len(image.shape) >= 3 and image.shape[2] >= 3


def to_gray(image):
    """Converts an image to gray scale.

    Applies .299 R + .587 G + .114 B .

    Args:
        image: The image to convert.
    Returns:
        The gray image. If the image only had one color dimension,
        the original image is returned.
    """
    if not is_color_image(image):
        return image
    return np.dot(image[..., :3], [.299, .587, .114])


def main():
    """Prints usage instructions."""
    print('Please use this file as an import and call the video loop:\n')
    print('\t%matplotlib notebook')
    print('\tfrom videoloop import videoloop\n')
    print('Remember that this package is designed to be invoked from a jupyter notebook.')
    exit(1)


if __name__ == '__main__':
    main()
