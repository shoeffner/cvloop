"""Provides a videoloop to be used in jupyter notebooks.

It automatically selects the notebook backend for matplotlib, if the
default notebook backend (inline) is detected.
"""

import itertools

import numpy as np
import cv2

import matplotlib
if matplotlib.get_backend() == 'module://ipykernel.pylab.backend_inline':
    matplotlib.use('nbAgg')

# Monkeypatch backend to include "pause" button and fire the pause_event.
from matplotlib.backends.backend_nbagg import NavigationIPy  # noqa: E402
NavigationIPy.toolitems += [('Pause', 'Pause/Resume video',
                             'fa fa-pause icon-pause', 'pause')]
NavigationIPy.pause = lambda self: self.canvas.callbacks.process('pause_event')

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.animation as animation  # noqa: E402
import matplotlib.image as image  # noqa: E402
import matplotlib.patches as patches  # noqa: E402


class cvloop(animation.TimedAnimation):
    """Uses a TimedAnimation to efficiently render video sources with blit."""

    def __init__(self, source=None, function=lambda x: x, *,
                 side_by_side=False, convert_color=cv2.COLOR_BGR2RGB,
                 cmaps=None, print_info=False, annotations=None,
                 annotations_default={'shape': 'RECT',
                                      'color': '#228B22',
                                      'line': 2,
                                      'size': (20, 20)}):
        """Runs a video loop for the specified source and modifies the stream
        with the function.

        The source can either be an integer for a webcam device, a string to
        load a video file or a VideoCapture object. In the last case, the
        capture object will not be released by this function.

        The function takes in a frame and returns the modified frame. The
        default value just passes the value through, it is equivalent to the
        identity function.

        If side_by_side is True, the input as well as the modified image are
        shown side by side, otherwise only the output is shown.

        If convert_color can be any value for cv2.cvtColor, e.g.
        cv2.COLOR_BGR2RGB.  If it is -1, no color conversion is performed,
        otherwise a color conversion using cv2.cvtColor is performed before the
        image is passed to the function.

        Args:
            source: The video source; ints for webcams/devices, a string to
                    load a video file. To fine tune a video source, it is
                    possible to pass a VideoCapture object directly.
                    (Default: 0)
            function: The modification function.
                      (Default: identity function `lambda x: x`)
            side_by_side: If True, both images are shown, the original and the
                          modified image.
                          (Default: False)
            convert_color: Converts the image with the given value using
                           `cv2.cvtColor`, unless value is -1.
                           (Default: `cv2.COLOR_BGR2RGB`)
            cmaps: If None, the plot function makes guesses about what color
                   maps to use (if at all). If a single value, that color map
                   is used for all plots (e.g. cmaps='gray').  If cmaps is a
                   tuple, the first value is used on the original image, the
                   second value for the modified image. If cmaps is a tuple,
                   None-entries are ignored and result in the normal guessing.
            print_info: If True, prints some info about the resource:
                        dimensions, color channels, data type. Skips the output
                        of one frame.
            annotations: A list or tuple of annotations. Each annotation is a
                         list or tuple in turn of this format:
                             [x, y, frame, options]
                         x: the x coordinate of the center
                         y: the y coordinate of the center
                         frame: the frame number
                         options: A dictionary. This is optional (leaving the
                             list with only three elements). Allows the
                             following keys:
                             shape: 'RECT' or 'CIRC' (rectangle, circle)
                             line: linewidth
                             color: RGB tuple, gray scalar or html hex-string
                             size: radius for CIRC, (width, height) for RECT
            annotations_default: A default format, that will be used if no
                    specific format is given for an annotation. If no format is
                    specified the following defaults are used:
                        shape: 'RECT',
                        color: '#228B22', (forestgreen)
                        line: 2,
                        size: (20, 20)
        """
        if source is not None:
            if isinstance(source, type(cv2.VideoCapture())) \
                    or hasattr(source, 'read'):
                self.capture = source
            else:
                with open('test.txt', 'w') as f:
                    print(source, file=f)
                self.capture = cv2.VideoCapture(source)
        else:
            self.capture = cv2.VideoCapture(0)

        self.figure = plt.figure()
        self.connect_event_handlers()

        self.function = function
        self.convert_color = convert_color

        self.annotations = (None if not annotations else
                            sorted(annotations, key=lambda a: a[2]))
        self.annotations_default = annotations_default
        self.annotation_artists = []

        self.original = None
        self.processed = None

        self.frame_offset = 0

        try:
            self.cmap_original = cmaps if isinstance(cmaps, str) else cmaps[0]
        except (IndexError, TypeError):
            self.cmap_original = None
        try:
            self.cmap_processed = cmaps if isinstance(cmaps, str) else cmaps[1]
        except (IndexError, TypeError):
            self.cmap_processed = None

        if side_by_side:
            axes_original = self.figure.add_subplot(1, 2, 1)
            axes_processed = self.figure.add_subplot(1, 2, 2)
        else:
            axes_original = None
            axes_processed = self.figure.add_subplot(1, 1, 1)

        if print_info:
            self.print_info(self.capture)

        self.size = self.determine_size(self.capture)
        self.original = self.__prepare_axes(axes_original, 'Original',
                                            self.size, self.cmap_original)
        self.processed = self.__prepare_axes(axes_processed, 'Processed',
                                             self.size, self.cmap_processed)

        self.axes_processed = axes_processed

        self.update_info()

        super().__init__(self.figure, interval=50, blit=True)
        plt.show()

    def connect_event_handlers(self):
        """Connects event handlers to the figure."""
        self.figure.canvas.mpl_connect('close_event', self.evt_release)
        self.figure.canvas.mpl_connect('pause_event', self.evt_toggle_pause)

    def evt_release(self, *args):
        """Tries to release the capture."""
        try:
            self.capture.release()
        except AttributeError:
            pass

    def evt_toggle_pause(self, *args):
        """Pauses and resumes the video source."""
        if self.event_source._timer is None:
            self.event_source.start()
        else:
            self.event_source.stop()

    def print_info(self, capture):
        """Prints information about the unprocessed image.

        Reads one frame from the source to determine image colors, dimensions
        and data types.

        Args:
            capture: the source to read from.
        """
        self.frame_offset += 1
        ret, frame = capture.read()
        if ret:
            print('Capture Information')
            print('\tDimensions (HxW): {}x{}'.format(*frame.shape[0:2]))
            print('\tColor channels:   {}'.format(frame.shape[2] if
                                                  len(frame.shape) > 2 else 1))
            print('\tColor range:      {}-{}'.format(np.min(frame),
                                                     np.max(frame)))
            print('\tdtype:            {}'.format(frame.dtype))
        else:
            print('No source found.')

    def determine_size(self, capture):
        """Determines the height and width of the image source.

        If no dimensions are available, this method defaults to a resolution of
        640x480, thus returns (480, 640).
        If capture has a get method it is assumed to understand
        `cv2.CAP_PROP_FRAME_WIDTH` and `cv2.CAP_PROP_FRAME_HEIGHT` to get the
        information. Otherwise it reads one frame from the source to determine
        image dimensions.

        Args:
            capture: the source to read from.

        Returns:
            A tuple containing integers of height and width (simple casts).
        """
        width = 640
        height = 480
        if capture and hasattr(capture, 'get'):
            width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        else:
            self.frame_offset += 1
            ret, frame = capture.read()
            if ret:
                width = frame.shape[1]
                height = frame.shape[0]
        return (int(height), int(width))

    def __prepare_axes(self, axes, title, size, cmap=None):
        """Prepares an axes object for clean plotting.

        Removes x and y axes labels and ticks, sets the aspect ratio to be
        equal, uses the size to determine the drawing area and fills the image
        with random colors as visual feedback.

        Creates an AxesImage to be shown inside the axes object and sets the
        needed properties.

        Args:
            axes:  The axes object to modify.
            title: The title.
            size:  The size of the expected image.
            cmap:  The colormap if a custom color map is needed.
                   (Default: None)
        Returns:
            The AxesImage's handle.
        """
        if axes is None:
            return None

        # prepare axis itself
        axes.set_xlim([0, size[1]])
        axes.set_ylim([size[0], 0])
        axes.set_aspect('equal')

        axes.axis('off')
        if isinstance(cmap, str):
            title = '{} (cmap: {})'.format(title, cmap)
        axes.set_title(title)

        # prepare image data
        axes_image = image.AxesImage(axes, cmap=cmap)
        axes_image.set_data(np.random.random((size[0], size[1], 3)))

        axes.add_image(axes_image)
        return axes_image

    def new_frame_seq(self):
        """Returns an endless frame counter.

        Starts at self.frame_offset, in case some methods had to read frames
        beforehand to gather information.

        This function is called by TimedAnimation.

        Returns:
            an endless frame count
        """
        return itertools.count(self.frame_offset)

    def _init_draw(self):
        """Initializes the drawing of the frames by setting the images to
        random colors.

        This function is called by TimedAnimation.
        """
        if self.original is not None:
            self.original.set_data(np.random.random((10, 10, 3)))
        self.processed.set_data(np.random.random((10, 10, 3)))

    def read_frame(self):
        """Reads a frame and converts the color if needed.

        In case no frame is available, i.e. self.capture.read() returns False
        as the first return value, the event_source of the TimedAnimation is
        stopped, and if possible the capture source released.

        Returns:
            None if stopped, otherwise the color converted source image.
        """
        ret, frame = self.capture.read()
        if not ret:
            self.event_source.stop()
            try:
                self.capture.release()
            except AttributeError:
                # has no release method, thus just pass
                pass
            return None
        if self.convert_color != -1 and self.is_color_image(frame):
            return cv2.cvtColor(frame, self.convert_color)
        return frame

    def process_frame(self, frame):
        """Processes a frame with the user specified function.

        Args:
            frame: The input frame.

        Returns:
            The processed frame.
        """
        return self.function(frame)

    def annotate(self, frame_no):
        """Annotates the processed axis with given annotations for
        the provided frame_no.

        Args:
            frame_no: The current frame number.
        """
        for artist in self.annotation_artists:
            artist.remove()
        self.annotation_artists = []
        for annotation in self.annotations:
            if annotation[2] > frame_no:
                return
            if annotation[2] == frame_no:
                pos = annotation[0:2]
                shape = self.annotations_default['shape']
                color = self.annotations_default['color']
                size = self.annotations_default['size']
                line = self.annotations_default['line']
                if len(annotation) > 3:
                    if 'shape' in annotation[3]:
                        shape = annotation[3]['shape']
                    if 'color' in annotation[3]:
                        color = annotation[3]['color']
                    if 'size' in annotation[3]:
                        size = annotation[3]['size']
                    if 'line' in annotation[3]:
                        line = annotation[3]['line']
                if shape == 'CIRC' and hasattr(size, '__len__'):
                    size = 30

                if not hasattr(color, '__len__'):
                    color = (color,) * 3

                if shape == 'RECT':
                    patch = patches.Rectangle((pos[0] - size[0] // 2,
                                               pos[1] - size[1] // 2),
                                              size[0], size[1], fill=False,
                                              lw=line, fc='none', ec=color)
                elif shape == 'CIRC':
                    patch = patches.CirclePolygon(pos, radius=size, fc='none',
                                                  ec=color, lw=line)
                self.annotation_artists.append(patch)
                self.axes_processed.add_artist(self.annotation_artists[-1])

    def _draw_frame(self, frame_no):
        """Reads, processes and draws the frames.

        If needed for color maps, conversions to gray scale are performed. In
        case the images are no color images and no custom color maps are
        defined, the colormap `gray` is applied.

        This function is called by TimedAnimation.

        Args:
            frame_no: The frame number.
        """
        original = self.read_frame()
        if original is None:
            self.update_info(self.info_string(message='Finished.',
                                              frame=frame_no))
            return

        if self.original is not None:
            processed = self.process_frame(original.copy())

            if self.cmap_original is not None:
                original = self.to_gray(original)
            elif not self.is_color_image(original):
                self.original.set_cmap('gray')
            self.original.set_data(original)
        else:
            processed = self.process_frame(original)

        if self.cmap_processed is not None:
            processed = self.to_gray(processed)
        elif not self.is_color_image(processed):
            self.processed.set_cmap('gray')

        if self.annotations:
            self.annotate(frame_no)

        self.processed.set_data(processed)

        self.update_info(self.info_string(frame=frame_no))

    def is_color_image(self, frame):
        """Checks if an image is a color image.

        A color image is an image with at least three dimensions and in the
        third dimension at least three color channels.

        Returns:
            True if the image is a color image.
        """
        return len(frame.shape) >= 3 and frame.shape[2] >= 3

    def to_gray(self, frame):
        """If the input is a color image, it is converted to gray scale.

        The first color channel is considered as R, the second as G, and
        the last as B. The gray scale image is then the weighted sum:

            gray = .299 R + .587 G + .114 B

        Returns:
            Either the converted image (if it was a color image) or the
            original.
        """
        if not self.is_color_image(frame):
            return frame
        return np.dot(frame[..., :3], [.299, .587, .114])

    def update_info(self, custom=None):
        """Updates the figure's suptitle.

        Calls self.info_string() unless custom is provided.

        Args:
            custom: Overwrite it with this string, unless None.
        """
        self.figure.suptitle(self.info_string() if custom is None else custom)

    def info_string(self, size=None, message='', frame=-1):
        """Returns information about the stream.

        Generates a string containing size, frame number, and info messages.
        Omits unnecessary information (e.g. empty messages and frame -1).

        This method is primarily used to update the suptitle of the plot
        figure.

        Returns:
            An info string.
        """
        info = []
        if size is not None:
            info.append('Size: {1}x{0}'.format(*size))
        elif self.size is not None:
            info.append('Size: {1}x{0}'.format(*self.size))
        if frame >= 0:
            info.append('Frame: {}'.format(frame))
        if message != '':
            info.append('{}'.format(message))
        return ' '.join(info)
