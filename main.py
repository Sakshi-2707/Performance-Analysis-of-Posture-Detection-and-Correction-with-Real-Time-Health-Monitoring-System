import tkinter as tk
import cv2
import mediapipe as mp
import threading
from Adafruit_IO import Client
from PIL import Image, ImageTk  # Import for background image handling

# Adafruit IO Configuration
aio = Client('Your adafruit profile name here', 'Write your adafruit API key here')

# MediaPipe Pose Solution
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Tkinter GUI Application
class ExerciseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spondylitis Exercise Detection and Correction")
        self.root.geometry("800x600")

        # Load background image
        self.bg_image = Image.open("C:\\Users\\saksh\\PycharmProjects\\pythonProject-adafuit\\Presentation1\\Slide1.JPG")# Replace with your image path
        self.bg_image = self.bg_image.resize((800, 600), Image.Resampling.LANCZOS)  # Resize the image to fit the window
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Create a background label
        self.bg_label = tk.Label(root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.exercise_var = tk.StringVar()

        # Problem Label (combined in one block, placed over the background)
        problem_text = "Problem: Spondylitis"
        tk.Label(root, text=problem_text, bg="lightblue", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)

        # Exercise Selection (aligned in the same row, placed over the background)
        tk.Label(root, text="Select Exercise:", bg="lightblue", font=("Arial", 12)).grid(row=0, column=1, padx=10, pady=10)
        exercises = ["Neck Stretch", "Shoulder Rolls", "Cat-Cow Stretch", "Torso Twist", "Seated Forward Bend"]
        self.exercise_menu = tk.OptionMenu(root, self.exercise_var, *exercises)
        self.exercise_menu.grid(row=0, column=2, padx=10, pady=10)

        # Start Exercise Button (aligned in the same row)
        tk.Button(root, text="Start Exercise", command=self.start_exercise, bg="lightyellow", font=("Arial", 12)).grid(row=0, column=3, padx=10, pady=10)

        # Video Display for the camera feed (on the second line)
        self.video_label = tk.Label(root, bg="lightgray")
        self.video_label.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

        # End Exercise Button (on the third line)
        tk.Button(root, text="End Exercise", command=self.end_exercise, bg="lightyellow", font=("Arial", 12)).grid(row=2, column=0, columnspan=4, padx=10, pady=10)

        # Variables for thread control
        self.camera_active = False

    def start_exercise(self):
        # Start the camera thread
        self.camera_active = True
        threading.Thread(target=self.camera_loop, daemon=True).start()

    def camera_loop(self):
        cap = cv2.VideoCapture(0)
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while self.camera_active and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Recolor the frame to RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Make detection
                results = pose.process(image)

                # Recolor back to BGR
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # Extract landmarks and draw
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                    # Perform posture checks based on specific exercise selected
                    self.check_posture(results.pose_landmarks)

                # Resize the image to fit the Tkinter window
                resized_image = cv2.resize(image, (640, 480))

                # Display the resulting image
                self.update_frame(resized_image)

                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()

    def update_frame(self, frame):
        """Convert the OpenCV frame to an ImageTk object and display it."""
        cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert the image to RGB format

        # Convert OpenCV image (NumPy array) to PIL image
        im_pil = Image.fromarray(cv2_image)

        # Convert PIL image to ImageTk format
        imgtk = ImageTk.PhotoImage(image=im_pil)

        # Update the Tkinter label with the image
        self.video_label.config(image=imgtk)
        self.video_label.image = imgtk  # Keep a reference to avoid garbage collection

    def check_posture(self, landmarks):
        # Check posture based on specific landmarks for each exercise
        pass  # Implement your posture validation logic here

    def end_exercise(self):
        # Stop video feed
        self.camera_active = False
        print("Exercise completed!")

# Main Tkinter Loop
root = tk.Tk()
app = ExerciseApp(root)
root.mainloop()
