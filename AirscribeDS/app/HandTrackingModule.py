import cv2
import mediapipe as mp

class handDetector():
    def __init__(self, mode = False, maxHands = 2, modelComplexity = 1, detectionCon = 0.5, trackCon = 0.5):
        # Initialize the handDetector class with default parameters for the hand tracking model
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        # Initialize the Mediapipe Hands module for hand tracking
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex, self.detectionCon, self.trackCon)
        # Initialize the drawing utilities for visualizing landmarks and connections
        self.mpDraw = mp.solutions.drawing_utils
        # Define the landmark IDs for the tips of the fingers
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw = True):
        # Convert the image to RGB format
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Process the image to detect hands using the hand tracking model
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            # If hands are detected, loop through each hand and draw landmarks and connections if draw is True
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        # Return the image with landmarks drawn
        return img

    def findPosition(self, img, handNo = 0, draw = True):
        self.lmList = []
        if self.results.multi_hand_landmarks:
            # If hands are detected, extract landmarks for the specified hand (handNo)
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                # Calculate the pixel coordinates (cx, cy) of each landmark
                cx, cy = int(lm.x*w), int(lm.y*h)
                self.lmList.append([id, cx, cy])
                if draw:
                    # Draw circles at the landmark positions if draw is True
                    cv2.circle(img, (cx,cy), 5, (255,0,0),cv2.FILLED)
        # Return the list of landmark positions
        return self.lmList

    def fingersUp(self):
        fingers = []
        # Check if the tip of the thumb is higher than the base of the thumb
        if self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0]-1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        # Check each finger (index, middle, ring, little) if the tip is higher than the base
        for id in range(1,5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        # Return a list indicating which fingers are up (1) or down (0)
        return fingers



























# def main():
#     cap = cv2.VideoCapture(0)
#     detector = handDetector()
#     while True:
#         success, img = cap.read()
#         img = cv2.flip(img,1)
#         img = detector.findHands(img)
#         lmList = detector.findPosition(img)
#         cv2.imshow("Image", img)
#         cv2.waitKey(1)
#
# def __name__ == "__main__":
#     main()
