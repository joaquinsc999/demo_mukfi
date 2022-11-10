import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
# VIDEO FEED
import pyttsx3
engine = pyttsx3.init()

def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle 

cap = cv2.VideoCapture(0)
## Setup mediapipe instance
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    reps = 0
    is_down = False
    prev_angle = 180
    prev_reps = None
    current_angle = 0
    deep = None
    top = None
    while cap.isOpened():
        ret, frame = cap.read()
        
        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
      
        # Make detection
        results = pose.process(image)
    
        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            angle = calculate_angle(ankle, knee, hip)

            """ if calculate_angle(ankle, knee, hip) <= 90 and not is_down:
                reps += 1
                print(reps)
                engine.say(reps)
                engine.runAndWait()
                is_down = True
            elif calculate_angle(ankle, knee, hip) > 90  and is_down:
                is_down = False """
            
            if angle < prev_angle + 5 and not is_down:
                prev_angle = angle
            elif angle < prev_angle + 5 and is_down:
                top = angle
                deep = None
                is_down = False
            elif angle > prev_angle + 5 and not is_down:
                deep = prev_angle
                is_down = True
                reps += 1
                print(reps)
                if deep > 90:
                    engine.say("You must go deeper")
                    engine.runAndWait()
                else:
                    engine.say(reps)
                    engine.runAndWait()
                top = None
            elif angle > prev_angle + 5 and is_down:
                prev_angle = angle
           
    
      
        
        except:
            pass
        
        
        # Render detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                 )               
        
        cv2.imshow('Mediapipe Feed', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


