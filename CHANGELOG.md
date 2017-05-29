# Changelog


## Version 0.3.4

- Adding annotation feature. Thanks @AndreaSuckro .
- Adding conda-forge support.


## Version 0.3.3

- Updating README.rst to reflect that Python 3.5 is no longer supported.
- `__version__` is accessed without importing everything.


## Version 0.3.2

- Uses some defaults to find the paths for the cascades. The path can be accessed using `cvloop.OPENCV_CASCADE_PATH`.
- Including LICENSE in package distribution.


## Version 0.3.1

* The webcam no longer takes precedence over video files.


## Version 0.3.0

* Classes instead of functions to handle state.
* DrawHat feature (by @JustinShenk)
* Video controls: Pause button + stop on figure closing.


## Version 0.2.0

* Animation with blits instead of draws.
* Matplotlib selects nbAgg if the backend is inline automatically
* Removing `%matplotlib notebook` from examples
* Updated documentation notebooks: removing `print_info`, as it is no longer supported.
* Added note about keeping a reference to the loop's return value


## Version 0.1.1

* Improved publishing process
* converted README.md to README.rst for pypi


## Version 0.1.0

* Shows webcam streams and allows to modify them.
