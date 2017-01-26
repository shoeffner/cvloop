cvloop
======

Provides cvloop, a way to show opencv video loops. Designed for jupyter notebooks.

**Simple example**: Show webcam feed.

.. code-block:: python

    from cvloop import cvloop
    cvloop()

**More complex example**: Show webcam feed side by side with inverted image.

.. code-block:: python

    from cvloop import cvloop
    cvloop(function=lambda frame: 255 - frame, side_by_side=True)

**Complex example**: Show video file with background extraction (See `OpenCV Documentation`_; `Video`_).

.. code-block:: python

    from cvloop import cvloop
    import cv2

    def mog2(frame):
        return mog2.fgbg.apply(frame)
    mog2.fgbg = cv2.createBackgroundSubtractorMOG2()

    cvloop('768x576.avi', function=mog2, side_by_side=True)

**More examples**: For more examples check out the `examples notebook`_.

Requirements
------------

(Recommended versions, additionally tested versions in parentheses)
-  Python 3.6 (3.5)
-  OpenCV 3.2 (3.1)
-  Jupyter 4.3.1

Dependencies
------------

-  matplotlib (2.0.0)
-  numpy (1.12.0)

.. _`OpenCV Documentation`: http://docs.opencv.org/3.1.0/db/d5c/tutorial_py_bg_subtraction.html
.. _`Video`: https://github.com/opencv/opencv_extra/tree/master/testdata/cv/video
.. _`examples notebook`: examples/cvloop_examples.ipynb

