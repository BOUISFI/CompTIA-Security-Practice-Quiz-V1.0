import os
import tkinter as tk
from tkinter import IntVar, font, ttk
import json
from PIL import Image, ImageTk
import threading
import time
import tkinter.messagebox as messagebox
from pygame import mixer
import random
import threading
from PIL import Image


# Global variable to keep track of the current track index
current_track_index = 0

# Global variable to signal the music thread to change the track
change_track_event = threading.Event()

# Initialize the mixer here
mixer.init()

# Add this dictionary at the beginning of your code
chapter_numbers = {
    "Chapter 1: Threats, Attacks, and Vulnerabilities": 1,
    "Chapter 2: Architecture and Design": 2,
    "Chapter 3: Implementation": 3,
    "Chapter 4: Operations and incident Response": 4,
    "Chapter 5: Governance, Risk, and Compliance": 5,
    "Generate Full Exam": 6,
}

class ChapterQuizGUI:
        
    def __init__(self, master, chapter_data, chapter_name):
        self.master = master
        self.chapter_data = chapter_data
        self.chapter_name = chapter_name
        self.image_window = None  # Initialize the image window attribute as None
        self.current_question = 0
        self.score = 0
        self.correctly_answered = [False] * len(chapter_data)  # List to track correct answers
        self.image_window = None  # Initialize the image window attribute as None

        #Exit Bind
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing) 

        #Review gui fix
        self.radio_vars = [tk.IntVar() for _ in range(len(self.chapter_data))]

        self.master.configure(bg="white")  # Set the background of the quiz window to white

        question_font = ("Helvetica", 10, "bold")  # Custom font for the question text
        choice_font = ("Helvetica", 10)  # Custom font for the choice text

        # Set the background of the question label to white
        self.question_label = tk.Label(self.master, 
                                       text="", 
                                       wraplength=700, 
                                       bg="white", 
                                       font=question_font,
                                       fg="red")  
        self.question_label.pack(pady=10)

        #setting Multichoices
        self.radio_var = IntVar()
        self.radio_var.set(-1)
        self.radio_buttons = []

        #Create a frame to hold the radio buttons
        radio_frame = tk.Frame(self.master, bg="white")
        radio_frame.pack()

        # Center the radio buttons horizontally
        for i in range(4):
            radio_button = tk.Radiobutton(radio_frame, 
                                          text="", 
                                          variable=self.radio_var, 
                                          value=i, bg="white",
                                          font=choice_font, 
                                          fg="red")
            radio_button.pack(pady=5)  # Adjust the padding value as needed
            self.radio_buttons.append(radio_button)

        #Adding next and previous Buttons
        self.previous_button = tk.Button(self.master, text="Previous", 
                                         bg="red", fg="white",
                                         command=self.previous_question,
                                         width=10)  # Set width for consistent button size
        self.next_button = tk.Button(self.master, text="Next", 
                                     bg="red", fg="white", 
                                     command=self.next_question,
                                     width=10)  # Set width for consistent button size
        
        #Padding Buttons
        self.previous_button.pack(side=tk.LEFT, padx=10)  
        self.next_button.pack(side=tk.RIGHT, padx=10)  
        
        #Return chapter Button
        self.return_button = tk.Button(self.master, 
                                       text="Return to Chapters", 
                                       bg="firebrick", 
                                       fg="white",
                                       command=self.return_to_chapters,
                                       width=50)  # Adjust width as needed
        self.return_button.pack(side=tk.BOTTOM, pady=(0, 100))
        
        #Submit Button
        self.submit_button = tk.Button(self.master, 
                                       text="Submit", 
                                       bg="red", 
                                       fg="white", 
                                       command=self.check_answer,
                                       width=15)
        self.submit_button.pack(side=tk.BOTTOM, pady=20)
        
        #Show image Button
        self.show_image_button = tk.Button(self.master, 
                                           text="Show Image", 
                                           bg="yellow", 
                                           fg="black", 
                                           command=self.show_image,
                                           width=60)
        self.show_image_button.pack(side=tk.BOTTOM, pady=10)

        #Timer 
        self.timer_label = tk.Label(self.master, bg="white", text="Time: 0:00", font=("Helvetica", 10))
        self.timer_label.pack(side=tk.TOP, pady=10) 

        # Create the music control button
        self.music_button = tk.Button(self.master, text="Pause Music", 
                                      command=self.toggle_music, 
                                      bg="black", 
                                      fg="white")
        self.music_button.pack(side=tk.TOP, pady=5)
        self.music_paused = False  # Flag to track if the music is paused

        # Create a button to randomize music
        randomize_button = tk.Button(self.master, text="Randomize Music ", command=self.randomize_music, bg="grey", fg="white")
        randomize_button.pack(side=tk.TOP, padx=5)

        # Create a label to display the current music track
        self.music_label = tk.Label(self.master, text="Music Player"+"", bg="white")
        self.music_label.pack(side=tk.TOP, padx=5)

        #Always at the end !
        self.show_question()

    #Closing fonction
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit the quiz? Your progress will be lost."):
            self.master.destroy()
            root.deiconify()
    
    #Music functions
    def toggle_music(self):
        if self.music_paused:
            mixer.music.unpause()  # Resume the music
            self.music_button.config(text="Pause Music")
            self.music_paused = False
        else:
            mixer.music.pause()  # Pause the music
            self.music_button.config(text="Play Music")
            self.music_paused = True
           
    def randomize_music(self):
        # Stop the current music
        mixer.music.stop()

        # Play random music
        music_folder = ".Music/"
        music_files = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]
        if music_files:
            selected_music = random.choice(music_files)
            music_track = os.path.join(music_folder, selected_music)
            mixer.music.load(music_track)
            mixer.music.set_volume(0.2)
            mixer.music.play(-1)  # Play indefinitely
            current_track_index = music_files.index(selected_music)

            # Update the music label
            self.music_label.config(text="Music Playing : " + selected_music)

            # Start the music loop thread
            music_thread = threading.Thread(target=self.play_music_loop)  # Remove the parentheses
            music_thread.daemon = True  # Set the thread as a daemon to exit when the main program exits
            music_thread.start()

    #Timer functions
    def start_timer_thread(self):
        self.timer_running = True
        self.start_time = time.time()
        timer_thread = threading.Thread(target=self.update_timer)
        timer_thread.start()

    def update_timer(self):
        while self.timer_running:
            elapsed_time = time.time() - self.start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            time_str = f"Time: {minutes}:{seconds:02}"
            self.timer_label.config(text=time_str)
            time.sleep(1)

    #Show question function
    def show_question(self):
        if self.current_question < len(self.chapter_data):
            question_data = self.chapter_data[self.current_question]
            question = question_data["question"]
            options = question_data["options"]

            #Update the correct_option variable
            self.correct_option = question_data["correct_option"]
            self.question_label.config(image=None)

            # Calculate the question number (increment by 1)
            question_number = self.current_question + 1

            # Display the question number along with the question text
            self.question_label.config(text=f"Question {question_number}: {question}")

            #Choices
            self.question_label.config(text=question)
            for i, option_text in enumerate(options):
                self.radio_buttons[i].config(text=option_text, variable=self.radio_vars[self.current_question])

            # Reset the selected radio button to no selection (-1)
            self.radio_vars[self.current_question].set(-1)

            #submit button
            self.submit_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.DISABLED)

            if self.current_question > 0:
                self.previous_button.config(state=tk.NORMAL)
            else:
                self.previous_button.config(state=tk.DISABLED)

            # Adding image
            image_path = self.chapter_data[self.current_question].get("image_filename", None)  # Use question_data instead of self.chapter_data
            #print("Image Path:", image_path)  # Add this line to print the image path
            if image_path:
                self.show_image_button.config(state=tk.NORMAL, bg="yellow", fg="black")
            else:
                self.show_image_button.config(state=tk.DISABLED, bg="grey", fg="white")
            #print("Question Data:", self.chapter_data[self.current_question])

        else:
            self.question_label.config(
                text="Quiz Completed! Your Score is: {}/{}".format(self.score, len(self.chapter_data)))
            for radio_button in self.radio_buttons:
                radio_button.config(state=tk.DISABLED)

            #Disable buttons    
            self.submit_button.config(state=tk.DISABLED)
            self.previous_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)

            #Show Review button
            self.review_button = tk.Button(self.master, text="Review Answers", bg="gold", fg="black",
                                           command=self.review_answers)
            self.review_button.pack(pady=10)


            #Self explanation button
            self.explanation_button = tk.Button(self.master, 
                                    text="View Explanation", 
                                    bg="Green", 
                                    fg="white",
                                    command=self.open_explanation,
                                    width=30)
            self.explanation_button.pack(side=tk.BOTTOM, pady=10)

            self.timer_running = False

    #Show Image function
    def show_image(self):
        image_path = self.chapter_data[self.current_question].get("image_filename", None)
        if image_path:
            if self.image_window:
                self.image_window.destroy()  # Close the existing image window if it's open
                
            original_image = Image.open(image_path)

            # Calculate the desired width and height based on the aspect ratio
            window_width = self.master.winfo_width()
            window_height = self.master.winfo_height()
            aspect_ratio = original_image.width / original_image.height
        
            max_width = window_width * 0.9  # Adjust the maximum width as needed
            max_height = window_height * 0.9  # Adjust the maximum height as needed
        
            # Calculate the dimensions while maintaining the aspect ratio
            if aspect_ratio > 1:  # Landscape-oriented image
                desired_width = int(max_width)
                desired_height = int(max_width / aspect_ratio)
            else:  # Portrait-oriented image
                desired_height = int(max_height)
                desired_width = int(max_height * aspect_ratio)

            resized_image = original_image.resize((desired_width, desired_height), resample=Image.LANCZOS)

            if self.image_window: self.image_window.destroy()
            image = ImageTk.PhotoImage(resized_image)
        
            image_window = tk.Toplevel(self.master)

            self.image_window = image_window  # Assign the image window to the attribute

            # Calculate the screen width and height
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()

            # Calculate the x and y positions to center the window
            x_position = (screen_width - desired_width) // 2
            y_position = (screen_height - desired_height) // 2

            # Set the window's geometry to be centered on the screen
            image_window.geometry("{}x{}+{}+{}".format(desired_width, desired_height, x_position, y_position))

            image_window.title("Question Image")
        
            image_label = tk.Label(image_window, image=image, bg="white")
            image_label.image = image
            image_label.pack(pady=10)
        else:
            print("No image available for this question.")

    #Show Review function
    def review_answers(self):
        review_window = tk.Toplevel(self.master)
        review_window.title("Review Answers")

        # Create a notebook (tabs) to display questions in groups of 5
        notebook = ttk.Notebook(review_window)
        notebook.pack(padx=10, pady=10)

        # Group questions into sets of 5 for each tab
        question_sets = [self.chapter_data[i:i+5] for i in range(0, len(self.chapter_data), 5)]

        for set_num, question_set in enumerate(question_sets):
            frame = ttk.Frame(notebook)
            frame.pack(fill="both", expand=True)

            # Display questions in the current set
            for i, (question_data, correctly_answered) in enumerate(zip(question_set, self.correctly_answered[set_num*5:(set_num+1)*5])):
                question = question_data["question"]
                options = question_data["options"]
                correct_option = question_data["correct_option"]  # Index of the correct option
                selected_option = self.radio_vars[set_num*5 + i].get()  # Use self.radio_vars[i].get() to get the selected option

                review_text = f"Question {set_num*5 + i + 1}: {question}\n"
                answer_text = "" 		

                if correctly_answered:
                    if selected_option == correct_option:
                        answer_text += f"Good Answer: {options[selected_option]} (Correct)\n"
                else:
                    answer_text += f"Your Answer: {options[selected_option]} (Incorrect)\n"
                    answer_text += f"Right Answer: {options[correct_option]} (Correct)\n"

                review_label = tk.Label(frame, text=review_text, wraplength=1000, font=("Helvetica", 10))
                review_label.pack(padx=20, pady=5)

                answer_label = tk.Label(frame, text=answer_text, wraplength=1000, font=("Helvetica", 10))
                answer_label.pack(padx=20, pady=2)

		
                # Color-coding based on correctness
                if "Incorrect" in answer_text :
                    answer_label.config(fg="red")
                elif "Correct" in answer_text :    
                    answer_label.config(fg="green")

            # Add the frame as a tab in the notebook
            notebook.add(frame, text=f"Questions {set_num*5 + 1}-{(set_num+1)*5}")

        # Calculate the screen width and height
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Calculate the x and y positions to center the window
        x_position = ((screen_width - review_window.winfo_reqwidth()) // 2) - 430
        y_position = ((screen_height - review_window.winfo_reqheight()) // 2)- 325

        # Set the window's geometry to be centered on the screen
        review_window.geometry(f"+{x_position}+{y_position}")

    #Check next previous & return functions
    def check_answer(self):
        selected_option = self.radio_vars[self.current_question].get()
        correct_option = self.chapter_data[self.current_question]["correct_option"]
        # Message box no select
        if selected_option == -1:
            messagebox.showinfo("Error", "Please select an answer before submitting.")  
            return
        
        if selected_option == correct_option:
            self.score += 1
            self.correctly_answered[self.current_question] = True  # Mark as correctly answered

        self.submit_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.NORMAL)
    
    # Open PDF explanation
    def open_explanation(self):
        if self.chapter_name == "Generate Full Exam":
            explanation_path = "Exp/Exam_Full.pdf"  # Use the combined explanation file for the full exam
        else:
            chapter_number = chapter_numbers.get(self.chapter_name, None)
        if chapter_number is not None:
            explanation_path = f"Chapter_{chapter_number}_Answer.pdf"
        else:
            messagebox.showinfo("Error", "Explanation not available for this chapter.")
            return

        try:
            os.startfile(explanation_path)  # Use "open" instead of "startfile" on macOS
        except Exception as e:
            print("Error opening PDF:", e)

    def next_question(self):
        if self.image_window:
            self.image_window.destroy()  # Close the image window if it's open
        self.current_question += 1
        self.show_question()

    def previous_question(self):
        self.current_question -= 1
        self.show_question()

    def return_to_chapters(self):
        # Ask for confirmation before returning to chapters
        confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to return to chapters? Your progress will be lost.")

        if confirmed:
            #pygame.mixer.music.stop()  # Stop the music
            self.master.destroy()
            # Restore the main window
            root.deiconify()

#Start quiz function (Second GUI)
def open_quiz_gui(chapter_data, chapter_name):

    quiz_window = tk.Toplevel(root)

    # Minimize the main window
    root.iconify()

    # Bind the restore function to the WM_DELETE_WINDOW event
    quiz_window.protocol("WM_DELETE_WINDOW", lambda: restore_main_window(quiz_window))
    
    # Calculate the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate the x and y positions to center the window
    x_position = (screen_width - 850) // 2
    y_position = (screen_height - 650) // 6

    # Set the window's geometry to be centered on the screen
    quiz_window.geometry("850x650+{}+{}".format(x_position, y_position))
    quiz_window.configure(bg="white")
    quiz_window.geometry("850x650")
    quiz_window.resizable(False, False)  # Disable resizing

    #Class call
    quiz_gui = ChapterQuizGUI(quiz_window, chapter_data, chapter_name) 

    #Timer
    quiz_gui.start_timer_thread()   
    
def restore_main_window(quiz_window):
    # Restore the main window
    root.deiconify()
    # Close the quiz window
    quiz_window.destroy()

#Play music
def play_music_loop():
    global current_track_index

    music_folder = ".Music/"
    music_files = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]
    while True:
        if change_track_event.wait():
            change_track_event.clear()

            current_track_index = (current_track_index + 1) % len(music_files)
            music_track = os.path.join(music_folder, music_files[current_track_index])
            mixer.music.load(music_track)
            mixer.music.set_volume(0.2)
            mixer.music.play(-1)

#Main GUI
def main_menu():
    # Initialize the music track index
    global current_track_index
    current_track_index = 0

    choice = messagebox.askquestion(
        "Welcome!",
        "Welcome to CompTIA Security+ Quiz made by Tarik Bouisfi.\n"
        "Let's set the mood for your quiz experience!\n\n"
        "And let's start some classical music for you to enjoy while passing the quiz!\n\n"
        "Do you want me to proceed with the music 'Yes', or to stop it 'No'?",
    )

    if choice == "no":
        mixer.music.pause()
    else:
        music_folder = ".Music/"
        music_files = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]
        if music_files:
            selected_music = random.choice(music_files)
            music_track = os.path.join(music_folder, selected_music)
            mixer.music.load(music_track)
            mixer.music.set_volume(0.2)
            mixer.music.play(-1)
            current_track_index = music_files.index(selected_music)

            # Start the music loop thread
            music_thread = threading.Thread(target=play_music_loop)
            music_thread.daemon = True  # Set the thread as a daemon to exit when the main program exits
            music_thread.start()

    explanation = "Welcome to the CompTIA Security+ SY0-601 Practice Quiz! " \
                  "\n<*>This quiz covers questions from David SEIDL's PRACTICE TESTS BOOK SECOND EDITION CompTIA Sec+. " \
                  "\n<**>For each chapter, you'll be presented with multiple-choice questions. " \
                  "Choose the correct option and click 'Submit'. You can review wrong questions at the end of every chapter,"\
                  "with the explination if you need it.\n Good luck with your studies!"
    custom_font = font.Font(family="Helvetica", size=9, weight="bold")
    explanation_label = tk.Label(root, text=explanation, wraplength=500, padx=10, pady=5, font=custom_font,
                                 bg="white", fg="red")
    explanation_label.pack(anchor="w", fill="both", padx=10, pady=0)

    root.configure(bg="white")
    for chapter, chapter_info in extracted_data.items():
        chapter_button = tk.Button(root, text=chapter, command=lambda f=chapter_info["questions"], c=chapter: load_and_start_quiz(f, c),
                                   bg="red", fg="white", padx=10, pady=5)
        chapter_button.pack(pady=10, anchor=tk.W)

    # Add a button for generating the exam in the main menu
    generate_exam_button = tk.Button(root, text="Generate Full Exam", command=generate_exam,
                                 bg="blue", fg="white", padx=10, pady=5)
    generate_exam_button.pack(pady=10, anchor=tk.W)    

    # Add name label
    name_label = tk.Label(root, text="Made by Tarik BOUISFI\n© 2023 All Rights Reserved.", font=("Helvetica", 8), bg="white", fg="black")
    name_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5, anchor=tk.S)

# Define the function to generate the exam
def generate_exam():
    total_questions = 10  # Total number of questions in the exam
    exam_duration = 6  # Exam duration in minutes

    # Calculate the number of questions from each chapter based on chapter objectives percentage
    questions_per_chapter = {}
    total_objectives_percentage = sum(chapter_info["objectives_percentage"] for chapter_info in extracted_data.values())
    
    # Initialize a variable to keep track of the total questions included
    total_questions_included = 0

    for chapter, chapter_info in extracted_data.items():
        objectives_percentage = chapter_info["objectives_percentage"]
        # Calculate the number of questions for this chapter based on percentage
        chapter_questions = round((objectives_percentage / total_objectives_percentage) * total_questions)
        
        # Ensure that the total questions do not exceed the desired total
        if total_questions_included + chapter_questions > total_questions:
            chapter_questions = total_questions - total_questions_included
        
        questions_per_chapter[chapter] = chapter_questions
        total_questions_included += chapter_questions

    # Create a list to store all exam questions
    exam_questions = []

    # Randomly select questions from each chapter based on the counts
    for chapter, chapter_info in extracted_data.items():
        chapter_questions = chapter_info["questions"]
        with open(chapter_questions, 'r') as json_file:
            chapter_data = json.load(json_file)
        
        random.shuffle(chapter_data)  # Shuffle the questions within the chapter
        selected_questions = chapter_data[:questions_per_chapter[chapter]]
        
        exam_questions.extend(selected_questions)
    
    # Start the exam GUI with the generated questions and exam_duration
    open_quiz_gui(exam_questions, "Full Exam")

#Jason load
def load_and_start_quiz(filename, chapter_name):
    with open(filename, 'r') as json_file:
        chapter_data = json.load(json_file)
    open_quiz_gui(chapter_data, chapter_name)  # Pass both arguments

#Main GUI banner and window
if __name__ == "__main__":
    root = tk.Tk()
    # Calculate the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate the x and y positions to center the window
    x_position = (screen_width - 800) // 2
    y_position = (screen_height - 500) // 2

    root.geometry("800x510+{}+{}".format(x_position, y_position))
    root.title("CompTIA Security+ Practice Quiz V1.0")
    root.resizable(False, False)  # Disable resizing
    
    # Add CompTIA Security+ logo on the left
    logo_image = tk.PhotoImage(file="comptia_logo.png")
    logo_label = tk.Label(root, image=logo_image)
    logo_label.image = logo_image
    logo_label.pack(side=tk.LEFT, padx=10, pady=10)
    
    #Question Data
    extracted_data = {
        "Chapter 1: Threats, Attacks, and Vulnerabilities": {"questions": ".Json/chapter1.json",
                                                              "explanation": "Exp/Chapter_1_Answer.pdf",
                                                              "objectives_percentage": 25,  # Adjust the percentage as needed
                                                              },
        "Chapter 2: Architecture and Design": {"questions": ".Json/chapter2.json",
                                                "explanation": "Exp/Chapter_2_Answer.pdf",
                                                "objectives_percentage": 20,  # Adjust the percentage as needed
                                                },
        "Chapter 3: Implementation": {"questions": ".Json/chapter3.json",
                                       "explanation": "Exp/Chapter_3_Answer.pdf",
                                       "objectives_percentage": 25,  # Adjust the percentage as needed
                                       },
        "Chapter 4: Operations and incident Response": {"questions": ".Json/chapter4.json",
                                                         "explanation": "Exp/Chapter_4_Answer.pdf", 
                                                         "objectives_percentage": 15,  # Adjust the percentage as needed
                                                        },
        "Chapter 5: Governance, Risk, and Compliance": {"questions": ".Json/chapter5.json",
                                                         "explanation": "Exp/Chapter_5_Answer.pdf",
                                                         "objectives_percentage": 15,  # Adjust the percentage as needed
                                                        },
    }

    main_menu()
    root.mainloop()
