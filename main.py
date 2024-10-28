import pyautogui
import time
import os
import io
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from PIL import Image
import keyboard
import pytesseract
import numpy as np
import random

# Set up for natural mouse movements
pyautogui.MINIMUM_DURATION = 0.3
pyautogui.MINIMUM_SLEEP = 0.1
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True


class WindowsAIUser:
    def __init__(self):
        self.llm = OllamaLLM(model="llava", url="http://localhost:11434")
        self.current_app = None
        self.last_click_time = time.time()
        self.action_history = []
        self.current_state = "initial"

    def move_naturally(self, x, y):
        x += random.randint(-5, 5)
        y += random.randint(-5, 5)
        pyautogui.moveTo(x, y, duration=random.uniform(0.3, 0.7))

    def type_naturally(self, text):
        for char in text:
            keyboard.write(char)
            time.sleep(random.uniform(0.05, 0.15))

    def analyze_screen(self, task):
        screenshot = pyautogui.screenshot()

        action_context = "\n".join(
            [f"- {action}" for action in self.action_history[-5:]]
        )

        prompt_template = """
        You are a Windows user trying to accomplish: {task}

        Previous actions taken:
        {action_context}

        Current state: {current_state}

        Looking at the current screen:
        [Screenshot is visible to you]

        Verify if the previous action has been completed.

        Important: Output only ONE single next action, not a list of steps .
        Example flows (but only output ONE next action):
        "Open notepad and type hello":
        If notepad not open -> START_APP: notepad
        If notepad visible but no text -> TYPE: hello
        If text typed -> TASK COMPLETE

        "Open Chrome and search cats":
        If Chrome not open -> START_APP: chrome
        If Chrome visible but empty -> TYPE: cats
        If text typed -> SHORTCUT: enter
        If results visible -> TASK COMPLETE

        Choose your ONE next action from:
        1. TYPE: <text> - Use this to type text
        2. WINDOWS - Use this to open start menu
        3. START_APP: <app_name> - Use this to launch specific apps
        4. CLICK: <x> <y> - Use this for mouse clicks at coordinates
        5. SHORTCUT: <keys> - Use this for keyboard shortcuts

        Format your response as a single line with just ONE action.
        """
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["task", "action_context", "current_state"],
        )

        action = self.llm.invoke(
            prompt.format(
                task=task,
                action_context=action_context,
                current_state=self.current_state,
            ),
            images=[screenshot],
        ).strip()

        self.action_history.append(action)
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

        elif action.startswith("CLICK:"):
            _, x, y = action.split()
            self.move_naturally(int(x), int(y))
            pyautogui.click()
            self.current_state = "clicking"

        elif action.startswith("SHORTCUT:"):
            keys = action.split(":")[1].strip()
            keyboard.press_and_release(keys)
            self.current_state = "shortcut"

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
