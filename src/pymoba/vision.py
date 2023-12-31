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


class PlatformCapture(ABC):
    """Abstract base class for capture objects"""

    def __init__(self):
        ...


class MacCapture(PlatformCapture):
    """Base class for capture objects on OSX"""

    def __init__(self):
        ...


class WindowsCapture(PlatformCapture):

    def __init__(self):
        super().__init__()


class ScreenCapture(ABC):
    """Abstract base class for high-level capture objects"""

    def __init__(self):
        pass

    @abstractmethod
    def get_windows(self):
        pass

    @abstractmethod
    def get_window_names(self):
        pass

    @abstractmethod
    def get_window_by_name(self, window_name: str):
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

    def display_screen_capture(self):
        """Display a realtime capture of the entire screen.

        Returns
        -------
        None
        """
        # While the loop isn't broken, display frame from screen capture
        start_time = time.time()
        while True:
            # frame = self.capture_frame()
            frame = self.capture_window_frame('pymoba – vision.py')
            cv2.imshow('Screen Capture', frame)
            # Display fps
            fps = 1 / (time.time() - start_time)
            print(f'FPS: {fps}')
            start_time = time.time()
            # Exit image capture and destroy windows when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break


class MacScreenCapture(ScreenCapture):
    """Concrete class to implement high-level capture object for mac"""

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

    def capture_frame(self):
        # Get bounds of chosen display - main display in this case
        monitor = CGDisplayBounds(CGMainDisplayID())
        # Define screenshot object that captures data from the chosen display
        screenshot = CGWindowListCreateImage(monitor,
                                             kCGWindowListOptionOnScreenOnly,
                                             kCGNullWindowID, kCGWindowImageDefault)

        if screenshot is None:
            raise ValueError("Could not create screenshot")

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
        # print(f'Window image:\n{window_image}')

        return window_image

    def image_from_window(self, window_id: int):
        screenshot = self._image_from_window(window_id)
        if screenshot is None:
            raise ValueError("Could not create screenshot")
        self.width = CGImageGetWidth(screenshot)
        self.height = CGImageGetHeight(screenshot)
        self.provider = CGImageGetDataProvider(screenshot)
        self.data = CGDataProviderCopyData(self.provider)
        self.bitmap = NSBitmapImageRep.alloc().initWithCGImage_(screenshot)
        self.bytes_per_row = self.bitmap.bytesPerRow()
        self.pixels_per_row = self.bytes_per_row // 4

        actual_width = len(self.data) // (self.height * 4)
        # Create image from captured data
        image = np.frombuffer(self.data, dtype=np.uint8)
        image.shape = (self.height, actual_width, 4)
        image = image[:, :actual_width, :]
        # Convert to cv2 image
        cv2_image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

        return cv2_image

    def capture_window_frame(self, window_name: str):
        window_info = self.get_window_by_name(window_name)
        if window_info:
            # Key should always exist if window exists
            # print(f'Found window by name: {window_name}')
            window_id = window_info['kCGWindowNumber']
            # print(f'Window id: {window_id}')
            return self.image_from_window(window_id)
        else:
            raise ValueError('No window found')


class WindowsScreenCapture(ScreenCapture):
    """Concrete class to implement high-level capture object for mac"""

    def __init__(self):
        super().__init__()

class ScreenCapture:

    def __init__(self):
        self.monitor = None
        self.width = None
        self.height = None
        self.provider = None
        self.data = None
        self.bitmap = None
        self.bytes_per_row = None
        self.pixels_per_row = None

    @staticmethod
    def get_windows():
        window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID)
        return window_list

    def get_window_names(self, windows: list | None = None):
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

    def capture_frame(self):
        # Get bounds of chosen display - main display in this case
        self.monitor = CGDisplayBounds(CGMainDisplayID())
        # Define screenshot object that captures data from the chosen display
        screenshot = CGWindowListCreateImage(self.monitor,
                                             kCGWindowListOptionOnScreenOnly,
                                             kCGNullWindowID, kCGWindowImageDefault)

        if screenshot is None:
            raise ValueError("Could not create screenshot")

        self.width = CGImageGetWidth(screenshot)
        self.height = CGImageGetHeight(screenshot)
        self.provider = CGImageGetDataProvider(screenshot)
        self.data = CGDataProviderCopyData(self.provider)
        self.bitmap = NSBitmapImageRep.alloc().initWithCGImage_(screenshot)
        self.bytes_per_row = self.bitmap.bytesPerRow()
        self.pixels_per_row = self.bytes_per_row // 4

        # Create image from captured data
        image = np.frombuffer(self.data, dtype=np.uint8)
        image.shape = (self.height, self.pixels_per_row, 4)
        image = image[:, :self.width, :]

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
        # print(f'Window image:\n{window_image}')

        return window_image

    def image_from_window(self, window_id: int):
        screenshot = self._image_from_window(window_id)
        if screenshot is None:
            raise ValueError("Could not create screenshot")
        self.width = CGImageGetWidth(screenshot)
        self.height = CGImageGetHeight(screenshot)
        self.provider = CGImageGetDataProvider(screenshot)
        self.data = CGDataProviderCopyData(self.provider)
        self.bitmap = NSBitmapImageRep.alloc().initWithCGImage_(screenshot)
        self.bytes_per_row = self.bitmap.bytesPerRow()
        self.pixels_per_row = self.bytes_per_row // 4

        actual_width = len(self.data) // (self.height * 4)
        # Create image from captured data
        image = np.frombuffer(self.data, dtype=np.uint8)
        image.shape = (self.height, actual_width, 4)
        image = image[:, :actual_width, :]
        # Convert to cv2 image
        cv2_image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

        return cv2_image

    def capture_window_frame(self, window_name: str):
        window_info = self.get_window_by_name(window_name)
        if window_info:
            # Key should always exist if window exists
            # print(f'Found window by name: {window_name}')
            window_id = window_info['kCGWindowNumber']
            # print(f'Window id: {window_id}')
            return self.image_from_window(window_id)
        else:
            raise ValueError('No window found')

    def display_screen_capture(self):
        # While the loop isn't broken, display frame from screen capture
        start_time = time.time()
        while True:
            # frame = self.capture_frame()
            frame = self.capture_window_frame('pymoba – vision.py')
            cv2.imshow('Screen Capture', frame)
            # Display fps
            fps = 1 / (time.time() - start_time)
            print(f'FPS: {fps}')
            start_time = time.time()
            # Exit image capture and destroy windows when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break


if __name__ == '__main__':
    capture = ScreenCapture()

    # Start and display live screen capture
    capture.display_screen_capture()

    # Get list of window names
    # window_names = capture.get_window_names()
    # print(f'\nWindow Names:\n{window_names}')

    # Get window details by window name
    # window_info = capture.get_window_by_name('pymoba – vision.py')
    # print(window_info)


