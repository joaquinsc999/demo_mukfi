import speech_recognition as sr
import pyttsx3
import datetime
import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)



def talk(text):
    engine.say(text)
    engine.runAndWait()

def calculate_angle(a,b,c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle 


def take_command():
    try:
        with sr.Microphone() as source:
            print('listening...')
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            print(command)
            if 'friday' in command:
                #command = command.replace('friday', '')
                print(command)
        
    except:
        command = None
        pass
    return command




def run_alexa():
    name = None
    while True:
        if not name:
            talk("Hello user, what's you're name?")
        while not name:
            command = take_command()
            if command:
                name = command
                print("user " +  command)
                talk(f"Hello {name} let's start")
                break 
        command = take_command()
        if command != None:
            if "count" in command and 'friday' in command:
                userPrefersLiveFeedBack = None
                talk("I'll be counting up to 5 reps, please prepare")
                talk(f"{name} would you like to have live feedback")
                while not userPrefersLiveFeedBack:
                    command = take_command()
                    if command:
                        if 'yes' in command or 'sure' in command:
                            userPrefersLiveFeedBack = True
                            talk("Cool let me set that for you")
                            break
                        elif 'no' in command:
                            userPrefersLiveFeedBack = False
                            talk("Got you")
                            break
                        elif not 'no' in command and not 'yes' in command and not 'sure' in command:
                            talk("Sorry, I didn't get that")
                           
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

                    while cap.isOpened() and reps < 5:
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
                                talk(reps)
                                is_down = True
                                if reps == 5:
                                    talk(f"Great {name}, you've finished")
                            elif calculate_angle(ankle, knee, hip) > 90  and is_down:
                                is_down = False """

                            if userPrefersLiveFeedBack:
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
                                        if reps == 5:
                                            talk(f"Great {name}, you've finished")
                                    else:
                                        engine.say(reps)
                                        engine.runAndWait()
                                        if reps == 5:
                                            talk(f"Great {name}, you've finished")
                                    top = None
                                elif angle > prev_angle + 5 and is_down:
                                    prev_angle = angle
                            else:
                                if calculate_angle(ankle, knee, hip) <= 90 and not is_down:
                                    reps += 1
                                    print(reps)
                                    talk(reps)
                                    is_down = True
                                    if reps == 5:
                                        talk(f"Great {name}, you've finished")
                                elif calculate_angle(ankle, knee, hip) > 90  and is_down:
                                    is_down = False
            
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
            elif "thank" in command:
                talk(f"You're welcome {name}, see you then")
                break
            elif ("shutdown" in command or "shut down" in command):
                talk(f"Shutting down the system, bye {name}")
                break
            elif 'how are you' in command:
                talk("I'm alright, nothing to complain about")
                pass
            elif 'give' in command and 'report' in command: 
                talk("I found 3 miskates on your squat, 1. You need to do it slower, 2. You need to have your back straight, and 3. You should load more weight.")
        else:
            pass
    


run_alexa()