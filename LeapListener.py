import Leap
from Leap import SwipeGesture, KeyTapGesture, Screen, ScreenList, InteractionBox
from pymouse import PyMouse

class LeapListener (Leap.Listener):

    def __init__ (self, parent):
        Leap.Listener.__init__ (self)
        self.parent = parent
        self.swipe_gesture = False
        self.swipe_id = 0
        self.mouse = PyMouse ()
        self.screen_height = self.mouse.screen_size()[1]
        self.screen_width = self.mouse.screen_size()[0]

    def on_init (self, controller):
        self.scroll_gesture = False

        print ("Initialized")

    def on_connect (self, controller):
        print ("Connected")

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)

    def on_disconnect (self, controller):
        print ("Disconnect")

    def on_exit (self, controller):
        print ("Exited")

    def on_frame (self, controller):
        """Does the heavy lifting of fingers and gestures"""
        frame = controller.frame ()

        # https://developer.leapmotion.com/documentation/Languages/Python/API/pydoc/Leap.InteractionBox.html#Leap.InteractionBox
        interaction_box = frame.interaction_box

        if (len(frame.fingers) != 0):

            if len(frame.fingers) == 1:
                # Move mouse based on fingers
                xPixel, yPixel = self.get_finger_pos (frame, interaction_box)
                self.mouse.move (xPixel, yPixel)
            elif len(frame.fingers) == 10:
                # Show gallery if 10 fingers are detected
                self.parent.stackedWidget.setCurrentIndex (0)

            for gesture in frame.gestures ():
                if gesture.type == Leap.Gesture.TYPE_SWIPE:
                    swipe = SwipeGesture (gesture)

                    self.parent.direction_x = swipe.direction.x

                    if self.parent.mode == "gallery":
                        # If the gallery is displayed scroll
                        self.parent.scroll_velocity = int(swipe.speed)
                        self.parent.setScroll (not self.parent.scroll)
                    else:
                        if len(frame.fingers) == 1 and swipe.state == Leap.Gesture.STATE_START:
                            # Using STATE_START will move only image forward or back
                            if swipe.direction.x > 0:
                                self.parent.previous_image ()
                            else:
                                self.parent.next_image ()

                elif gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                    
                    if len(frame.fingers) == 1:
                        self.mouse.click (self.mouse.position ()[0], self.mouse.position ()[1])

    def get_finger_pos (self, frame, interaction_box):
        """Map finger position to screen position"""
        finger = frame.fingers[0]
        normalizedCoordinates = interaction_box.normalize_point (finger.tip_position, False)

        xPixel = normalizedCoordinates.x * self.screen_width
        yPixel = self.screen_height - (normalizedCoordinates.y * self.screen_height)

        return (xPixel, yPixel)
