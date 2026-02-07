import cv2
import mediapipe as mp
import pyautogui
import math
import time
import numpy as np

# --- Configuration ---
width_cam, height_cam = 640, 480
frame_reduction = 100

# Tuning
min_smooth = 2
max_smooth = 15
jitter_dist = 3
scroll_speed = 20

# --- CHANGE: SCROLL LINE POSITION ---
# Moved line higher (150px from top) so it's distinct from the resting position
scroll_line_y = 150  

# Click Settings
click_threshold = 40
click_cooldown = 0.5
right_click_cooldown = 1.0
safety_delay = 2.0         # 2s wait for Left Click after Fist

# --- CRITICAL SETTINGS ---
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# --- Setup ---
cap = cv2.VideoCapture(0)
cap.set(3, width_cam)
cap.set(4, height_cam)

hand_detector = mp.solutions.hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
drawing_utils = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()

# State Variables
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0
last_left_click = 0
last_right_click = 0 
fist_start_time = 0
program_start_time = time.time()

def is_fist(landmarks):
    """Checks if a hand is a fist."""
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    fingers_down = 0
    for i in range(len(tips)):
        if landmarks[tips[i]].y > landmarks[pips[i]].y:
            fingers_down += 1
    return fingers_down == 4

def fingers_up(landmarks):
    """Returns list of booleans [Thumb, Index, Middle, Ring, Pinky]"""
    status = []
    if landmarks[4].x < landmarks[3].x: status.append(True)
    else: status.append(False)
    
    tips = [8, 12, 16, 20]
    for id in tips:
        if landmarks[id].y < landmarks[id-2].y: status.append(True)
        else: status.append(False)
    return status

print("System Ready.")
print("Left Hand: 1 Finger=Move, 2 Fingers=Scroll.")
print("Right Hand: Pinch=Left Click, FIST=Right Click.")

while True:
    success, frame = cap.read()
    if not success: break
    
    frame = cv2.flip(frame, 1) 
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = hand_detector.process(rgb_frame)
    hands = output.multi_hand_landmarks
    
    # Draw Scroll Line (Purple)
    cv2.line(frame, (0, scroll_line_y), (width_cam, scroll_line_y), (255, 0, 255), 2)
    
    # --- 1. Global Exit Check (Hold 2 Fists for 5s) ---
    fist_count = 0
    if hands:
        for hand in hands:
            if is_fist(hand.landmark): fist_count += 1

    if fist_count == 2:
        if fist_start_time == 0: fist_start_time = time.time()
        elapsed = time.time() - fist_start_time
        remaining = 5 - int(elapsed)
        cv2.putText(frame, f"EXIT IN: {remaining}s", (width_cam//2 - 100, height_cam//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        if elapsed > 5:
            print("Exiting...")
            break
    else:
        fist_start_time = 0

    # --- 2. Hand Processing ---
    if hands:
        for index, hand_info in enumerate(output.multi_handedness):
            hand_label = hand_info.classification[0].label
            landmarks = hands[index].landmark
            
            index_x = int(landmarks[8].x * frame_width)
            index_y = int(landmarks[8].y * frame_height)
            thumb_x = int(landmarks[4].x * frame_width)
            thumb_y = int(landmarks[4].y * frame_height)
            middle_y = int(landmarks[12].y * frame_height)

            # --- LEFT HAND: NAVIGATION ---
            if hand_label == "Left":
                fingers = fingers_up(landmarks)
                
                # Scroll Mode
                if fingers[1] and fingers[2]:
                    cv2.putText(frame, "SCROLL", (index_x, index_y - 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
                    
                    # Logic: Hand ABOVE line = Scroll UP
                    if middle_y < scroll_line_y - 20: 
                        pyautogui.scroll(scroll_speed)
                    # Logic: Hand BELOW line = Scroll DOWN
                    elif middle_y > scroll_line_y + 20: 
                        pyautogui.scroll(-scroll_speed)

                # Move Mode
                elif fingers[1]:
                    target_x = np.interp(index_x, (frame_reduction, width_cam - frame_reduction), (0, screen_width))
                    target_y = np.interp(index_y, (frame_reduction, height_cam - frame_reduction), (0, screen_height))
                    
                    dist_move = math.hypot(target_x - prev_x, target_y - prev_y)
                    if dist_move < jitter_dist:
                        target_x = prev_x
                        target_y = prev_y
                    
                    speed_factor = min(1.0, dist_move / 150) 
                    current_smooth = max_smooth - (speed_factor * (max_smooth - min_smooth))
                    
                    curr_x = prev_x + (target_x - prev_x) / current_smooth
                    curr_y = prev_y + (target_y - prev_y) / current_smooth
                    
                    pyautogui.moveTo(curr_x, curr_y)
                    prev_x, prev_y = curr_x, curr_y
                    cv2.circle(frame, (index_x, index_y), 8, (0, 255, 255), cv2.FILLED)

            # --- RIGHT HAND: CLICKS ---
            if hand_label == "Right":
                dist_pinch = math.hypot(index_x - thumb_x, index_y - thumb_y)
                right_hand_fist = is_fist(landmarks)

                # 1. Right Click (Right Hand Fist)
                if right_hand_fist and fist_count != 2:
                    cv2.putText(frame, "RIGHT CLICK", (index_x, index_y - 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                    if time.time() - last_right_click > right_click_cooldown:
                        pyautogui.rightClick()
                        last_right_click = time.time()
                        print("Right Click (Fist)")
                
                # 2. Left Click (Pinch)
                elif dist_pinch < click_threshold:
                    time_since_right = time.time() - last_right_click
                    
                    # Only allow Left Click if 2 seconds have passed since Right Click
                    if time_since_right > safety_delay:
                        cv2.circle(frame, (index_x, index_y), 15, (0, 255, 0), cv2.FILLED)
                        if time.time() - last_left_click > click_cooldown:
                            pyautogui.click()
                            last_left_click = time.time()
                            print("Left Click")
                    else:
                        wait_time = round(safety_delay - time_since_right, 1)
                        cv2.putText(frame, f"Wait {wait_time}s", (index_x, index_y - 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

    cv2.rectangle(frame, (frame_reduction, frame_reduction), 
                 (width_cam - frame_reduction, height_cam - frame_reduction), (255, 0, 255), 2)
    
    cv2.imshow('Virtual Mouse', frame)
    if cv2.waitKey(1) == ord('q'): break

cap.release()
cv2.destroyAllWindows()
