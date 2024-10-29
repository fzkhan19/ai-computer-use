import pyautogui
import time
from langchain_ollama import OllamaLLM
import keyboard
import random
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Set up for natural mouse movements
pyautogui.MINIMUM_DURATION = 0.3
pyautogui.MINIMUM_SLEEP = 0.1
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True


class WindowsAIUser:
    def __init__(self):
        self.llava = OllamaLLM(model="llava", url="http://localhost:11434")
        gemini_key = os.getenv("GEMINI_API_KEY")

        # Initialize Gemini with API key
        genai.configure(api_key=gemini_key)
        self.gemini = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            api_key=gemini_key,
        )

        self.current_app = None
        self.last_click_time = time.time()
        self.action_history = []
        self.current_state = "initial"

    def log_response(self, model_name, response):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("ai_responses.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"\n{'='*50}\n")
            log_file.write(f"Timestamp: {timestamp}\n")
            log_file.write(f"Model: {model_name}\n")
            log_file.write(f"Response:\n{response}\n")
            log_file.write(f"{'='*50}\n")

    def move_naturally(self, x, y):
        x += random.randint(-5, 5)
        y += random.randint(-5, 5)
        pyautogui.moveTo(x, y, duration=random.uniform(0.3, 0.7))

    def type_naturally(self, text):
        for char in text:
            keyboard.write(char)
            time.sleep(random.uniform(0.05, 0.15))

    def llava_query(self, prompt):
        # Method to let Gemini query Llava with a specific prompt
        screenshot = pyautogui.screenshot()
        query_prompt = "According to the provided screenshot" + prompt
        response = self.llava.invoke(query_prompt, images=[screenshot])
        self.log_response("LLaVa (Queried by Gemini)", response)
        return response

    def analyze_screen(self, task):
        self.llava.invoke("/clear")
        screenshot = pyautogui.screenshot()

        # Direct vision prompt for LLaVa
        vision_prompt = """You are looking at a Windows 11 computer screen screenshot.
        Analyze this Windows 11 screenshot and list:
        1. All visible windows with their titles
        2. Location of UI elements (buttons, text fields, icons)
        3. Any visible text content
        4. Current active window or focused element
        5. Windows 11 taskbar state and visible icons
        6. Start menu state if visible

        Format as a clear, factual list focusing on Windows 11 UI elements."""

        screen_description = self.llava.invoke(vision_prompt, images=[screenshot])
        self.log_response("LLaVa", screen_description)

        print("\n::::: LLAVA Screen description :::::\n", screen_description)

        reasoning_prompt = f"""
        Role: You are a Windows 11 User and you have to perform the given task using the provided set of actions.
        Task to accomplish: {task}

        Previous actions taken:
        {"\n".join([f"- {action}" for action in self.action_history[-5:]])}

        Current state: {self.current_state}

        Screen description:
        {screen_description}

        Available actions and their effects:
        1. TYPE: <text> - Types the specified text with natural typing speed and random delays
        2. WINDOWS - Presses Windows key to open/close Start menu
        3. START_APP: <app_name> - Opens Windows Start menu, searches for app, and launches it
        4. PRESS_KEY: <key> - Presses a single keyboard key (e.g., enter, tab, space)
        5. CLICK: <x> <y> - Moves mouse naturally to coordinates and clicks (you can ask LLaVa for coordinates based on the screen size 1920x1080)
        6. SHORTCUT: <keys> - Executes keyboard shortcuts (e.g., ctrl+c, alt+tab)
        7. QUERY_LLAVA: <specific question> - Asks LLaVa to analyze specific details in the current screen
        8. TASK COMPLETE - Indicates the requested task has been successfully completed

        If additional specific information is required from the screen, specify the prompt to query LLaVa.
        Provide exactly ONE next action from the options above.

        Output format: Single line with just the action."""

        action = self.gemini.invoke(reasoning_prompt).content.strip()
        self.log_response("Gemini", action)

        print("\n::::: GEMINI Action :::::\n", action)
        self.action_history.append(action)

        # If Gemini requests specific info from LLaVa
        if action.startswith("QUERY_LLAVA:"):
            specific_query = action.split(":", 1)[1].strip()
            return f"QUERY_LLAVA: {specific_query}"

        return action

    def execute_action(self, action):
        if action.startswith("TYPE:"):
            text = action.split(":")[1].strip()
            self.type_naturally(text)
            self.current_state = "typing"

        elif action == "WINDOWS":
            keyboard.press_and_release("win")
            time.sleep(random.uniform(0.5, 1))
            self.current_state = "start_menu"

        elif action.startswith("START_APP:"):
            app = action.split(":")[1].strip()
            keyboard.press_and_release("win")
            time.sleep(0.5)
            self.type_naturally(app)
            time.sleep(0.5)
            keyboard.press_and_release("enter")
            self.current_state = f"launching_{app}"

        elif action.startswith("PRESS_KEY:"):
            key = action.split(":")[1].strip()
            keyboard.press_and_release(key)
            self.current_state = f"pressing_key_{key}"

        elif action.startswith("CLICK:"):
            _, x, y = action.split()
            self.move_naturally(int(x), int(y))
            pyautogui.click()
            self.current_state = "clicking"

        elif action.startswith("SHORTCUT:"):
            keys = action.split(":")[1].strip()
            keyboard.press_and_release(keys)
            self.current_state = "shortcut"

        elif action.startswith("QUERY_LLAVA:"):
            specific_query = action.split(":", 1)[1].strip()
            llava_response = self.llava_query(specific_query)
            print("\n::::: LLAVA Query Response :::::\n", llava_response)
            self.log_response("LLaVa Query Result", llava_response)

        time.sleep(random.uniform(0.5, 1))
        return True


def main():
    print("Program started. Press 'esc' to stop at any time.")
    keyboard.on_press_key("esc", lambda _: exit())

    ai_user = WindowsAIUser()

    while True:
        print("\nWhat task should I perform?")
        task = input("> ")

        if task.lower() in ["exit", "quit", "stop"]:
            break

        max_attempts = 30
        attempt = 0

        while attempt < max_attempts:
            action = ai_user.analyze_screen(task)
            print(f"Taking action: {action}")

            if action == "TASK COMPLETE":
                print("Task completed successfully!")
                ai_user.action_history = []  # Reset history for new task
                ai_user.current_state = "initial"
                break

            if ai_user.execute_action(action):
                attempt += 1

            time.sleep(random.uniform(0.5, 1))

        if attempt >= max_attempts:
            print("Maximum attempts reached")


if __name__ == "__main__":
    main()
