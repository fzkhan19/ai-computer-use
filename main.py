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
        # Add slight randomness to movement
        x += random.randint(-5, 5)
        y += random.randint(-5, 5)
        pyautogui.moveTo(x, y, duration=random.uniform(0.3, 0.7))

    def type_naturally(self, text):
        for char in text:
            keyboard.write(char)
            time.sleep(random.uniform(0.05, 0.15))

    def analyze_screen(self, task):
        screenshot = pyautogui.screenshot()
        # Create context from action history
        action_context = "\n".join(
            [f"- {action}" for action in self.action_history[-5:]]
        )  # Last 5 actions

        prompt_template = """
        You are a Windows user trying to accomplish: {task}

        Previous actions taken:
        {action_context}

        Current state: {current_state}

        Looking at the current screen:
        [Screenshot is visible to you]

        Respond with exactly ONE action from this list:
        1. TYPE: <text> - Use this to type text
        2. WINDOWS - Use this to open start menu
        3. START_APP: <app_name> - Use this to launch specific apps
        4. CLICK: <x> <y> - Use this for mouse clicks at coordinates
        5. SHORTCUT: <keys> - Use this for keyboard shortcuts
        6. TASK COMPLETE - Use this when the task is finished

        Format your response as a single line with just the action.
        Example responses:
        START_APP: chrome
        TYPE: hello world
        WINDOWS
        CLICK: 500 400
        SHORTCUT: alt+tab
        Consider the previous actions and current screen to make progress towards the goal.
        Don't repeat unsuccessful actions.

        What is your next action?
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

        elif action == "WINDOWS":
            keyboard.press_and_release("win")
            time.sleep(random.uniform(0.5, 1))

        elif action.startswith("START_APP:"):
            app = action.split(":")[1].strip()
            keyboard.press_and_release("win")
            time.sleep(0.5)
            self.type_naturally(app)
            time.sleep(0.5)
            keyboard.press_and_release("enter")

        elif action.startswith("CLICK:"):
            _, x, y = action.split()
            self.move_naturally(int(x), int(y))
            pyautogui.click()

        elif action.startswith("SHORTCUT:"):
            keys = action.split(":")[1].strip()
            keyboard.press_and_release(keys)

        time.sleep(random.uniform(0.5, 1))
        return True


def main():
    # Add keyboard failsafe
    print("Program started. Press 'esc' to stop at any time.")
    keyboard.on_press_key("esc", lambda _: exit())

    ai_user = WindowsAIUser()
    print("What task should I perform?")
    task = input("> ")

    max_attempts = 30
    attempt = 0

    while attempt < max_attempts:
        action = ai_user.analyze_screen(task)
        print(f"Taking action: {action}")

        if ai_user.execute_action(action):
            attempt += 1

        if "TASK COMPLETE" in action:
            print("Task completed successfully!")
            break

        time.sleep(random.uniform(0.5, 1))

    if attempt >= max_attempts:
        print("Maximum attempts reached")


if __name__ == "__main__":
    main()
