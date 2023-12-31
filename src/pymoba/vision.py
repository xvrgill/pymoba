import cv2
import numpy as np
from Quartz.CoreGraphics import (
    CGWindowListCreateImage,
    CGDisplayBounds,
    CGMainDisplayID,
    CGRectNull
)
from Quartz import (
    kCGNullWindowID,
    kCGWindowImageDefault,
    kCGWindowListOptionOnScreenOnly,
    CGImageGetWidth,
    CGImageGetHeight,
    CGImageGetDataProvider,
    CGDataProviderCopyData,
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionIncludingWindow,
    kCGWindowListOptionAll
)
from Cocoa import NSBitmapImageRep
import time
from abc import ABC, abstractmethod
import platform


class PlatformCapture(ABC):
    """Abstract base class for capture objects"""

    def __init__(self):
        super().__init__()

    @staticmethod
    @abstractmethod
    def get_windows():
        pass

    @abstractmethod
    def get_window_names(self):
        pass

    @abstractmethod
    def get_window_by_name(self, window_name: str):
        pass

    @abstractmethod
    def get_window_by_id(self, window_id: int):
        pass

    @abstractmethod
    def capture_frame(self):
        pass

    @abstractmethod
    def image_from_window(self, window_id: int):
        pass

    @abstractmethod
    def capture_window_frame(self, window_name: str):
        pass

    @staticmethod
    def _open_live_capture(frame, start_time: float):
        cv2.imshow('Screen Capture', frame)
        # Display fps
        fps = 1 / (time.time() - start_time)
        print(f'FPS: {fps}')
        return time.time()

    def capture_display(self):
        """Display a realtime capture of the entire screen.

        Returns
        -------
        None
        """
        # While the loop isn't broken, display frame from screen capture
        start_time = time.time()
        while True:
            frame = self.capture_frame()
            start_time = self._open_live_capture(frame, start_time)
            # Exit image capture and destroy windows when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

    def capture_window(self, window_name: str):
        """Display a realtime capture of the entire screen.

        Returns
        -------
        None
        """
        # While the loop isn't broken, display frame from screen capture
        start_time = time.time()
        while True:
            frame = self.capture_window_frame(window_name)
            cv2.imshow('Screen Capture', frame)
            start_time = self._open_live_capture(frame, start_time)
            # Exit image capture and destroy windows when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break


class MacCapture(PlatformCapture):
    """Base class for capture objects on OSX"""

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_windows():
        window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
        return window_list

    def get_window_names(self, windows: list | None = None):
        """Retrieve names of all windows.

        Parameters
        ----------
        windows: list
            list of window mappings

        Returns
        -------
        list of names of all windows
        """
        if windows is None:
            w = self.get_windows()
        else:
            w = windows

        return [window.get('kCGWindowName', '') for window in w]

    def get_window_by_name(self, window_name: str):
        windows = self.get_windows()
        for window in windows:
            if window.get('kCGWindowName', '') == window_name:
                return window
        return None

    def get_window_by_id(self, window_id: int):
        windows = self.get_windows()
        for window in windows:
            if window['kCGWindowNumber'] == window_id:
                return window
        return None

    def capture_frame(self):
        # Get bounds of chosen display - main display in this case
        monitor = CGDisplayBounds(CGMainDisplayID())
        # Define screenshot object that captures data from the chosen display
        screenshot = CGWindowListCreateImage(monitor,
                                             kCGWindowListOptionOnScreenOnly,
                                             kCGNullWindowID, kCGWindowImageDefault)

        # Handle case where frame couldn't be created
        if screenshot is None:
            raise ValueError("Could not create screenshot")

        # Extract required data from image object
        width = CGImageGetWidth(screenshot)
        height = CGImageGetHeight(screenshot)
        provider = CGImageGetDataProvider(screenshot)
        data = CGDataProviderCopyData(provider)
        bitmap = NSBitmapImageRep.alloc().initWithCGImage_(screenshot)
        bytes_per_row = bitmap.bytesPerRow()
        pixels_per_row = bytes_per_row // 4

        # Create image from captured data
        image = np.frombuffer(data, dtype=np.uint8)
        image.shape = (height, pixels_per_row, 4)
        image = image[:, :width, :]

        # Convert to cv2 image
        cv2_image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

        return cv2_image

    @staticmethod
    def _image_from_window(window_id):
        window_image = CGWindowListCreateImage(
            CGRectNull,  # Capture the whole screen
            kCGWindowListOptionIncludingWindow,
            window_id,
            kCGWindowImageDefault
        )

        return window_image

    def image_from_window(self, window_id: int):
        screenshot = self._image_from_window(window_id)
        if screenshot is None:
            raise ValueError("Could not create screenshot")
        # width = CGImageGetWidth(screenshot)
        height = CGImageGetHeight(screenshot)
        provider = CGImageGetDataProvider(screenshot)
        data = CGDataProviderCopyData(provider)
        # Need to use new calculation to handle pixel counts that aren't 64 divisible
        # total_elem = height * width * 4
        # Can calculate the actual width via basic algebra
        actual_width = len(data) // (height * 4)
        # Create image from captured data
        image = np.frombuffer(data, dtype=np.uint8)
        image.shape = (height, actual_width, 4)
        image = image[:, :actual_width, :]
        # Convert to cv2 image
        cv2_image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

        return cv2_image

    def capture_window_frame(self, window_name: str):
        window_info = self.get_window_by_name(window_name)
        if window_info:
            # Key should always exist if window exists
            window_id = window_info['kCGWindowNumber']
            # Use the following code for LOL
            # Need to get window by id because multiple share the same name
            # Window will have the size set in the client. Look for that size.
            # return self.image_from_window(16789)
            return self.image_from_window(window_id)
        else:
            raise ValueError('No window found')


class WindowsCapture(PlatformCapture):

    def __init__(self):
        super().__init__()

    def get_windows(self):
        pass

    def get_window_names(self):
        pass

    def get_window_by_name(self, window_name: str):
        pass

    def get_window_by_id(self, window_id: int):
        pass

    def capture_frame(self):
        pass

    def image_from_window(self, window_id: int):
        pass

    def capture_window_frame(self, window_name: str):
        pass


class ScreenCapture:

    def __init__(self):
        super().__init__()
        self.capture = self.create_capture()

    @property
    def _platform(self):
        return platform.system()

    # TODO: Separate out screen and window captures into concrete class implementations
    def create_capture(self):
        _platform = self._platform
        if _platform == 'Darwin':
            return MacCapture()
        elif _platform == 'Windows':
            raise NotImplementedError('Windows is not currently supported')


if __name__ == '__main__':
    sc = ScreenCapture()
    capture = sc.capture

    # Start and display live screen capture
    # capture.capture_display()

    # Start and display window screen capture
    # capture.capture_window('League of Legends')
    capture.capture_window('<Window Name>')

    # Get list of windows
    # windows = capture.get_windows()
    # print(windows)

    # Get list of window names
    # window_names = capture.get_window_names()
    # print(f'\nWindow Names:\n{window_names}')

    # Get window details by window name
    # window_info = capture.get_window_by_name('League of Legends')
    # print(window_info)

    # Get window details by window id
    # window_info = capture.get_window_by_id(9910)
    # print(window_info)
