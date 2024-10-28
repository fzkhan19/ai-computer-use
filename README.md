### README.md for **AI Computer User**

---

# AI Computer User

An experimental script for using AI to interact with Windows applications through natural mouse movements, keystrokes, and intelligent screen analysis. With the help of **LangChain**, **PyAutoGUI**, and **PyTesseract**, this project automates tasks based on real-time visual and contextual information, enabling a pseudo-user experience powered by an AI-driven approach.

## Features

- **Natural Interaction**: Simulates human-like mouse movements and typing delays.
- **Task-Specific Execution**: Analyzes the current screen and determines one actionable step for task completion.
- **Incremental Task Handling**: Builds upon previous actions to complete complex, multi-step tasks.
- **Screenshot-Based Analysis**: Uses screenshots to verify the interface state and take appropriate actions.
- **Customizable Actions**: Adapts actions based on contextual clues for a seamless, stepwise task approach.

## Getting Started

### Prerequisites

- **Python 3.x**
- **LangChain Ollama** - Run an Ollama LLM model locally.
- **Required Libraries**:
  - `pyautogui`, `keyboard`, `pytesseract`, `numpy`, `Pillow`, `random`, `time`

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/fzkhan19/ai-computer-use.git
    cd ai-computer-use
    ```

2. **Install Dependencies:**
    ```bash
    pip install pyautogui keyboard pillow langchain_ollama pytesseract numpy
    ```

3. **Set Up LangChain Ollama Model:**
    - Start the Ollama LLM server locally at `http://localhost:11434`.

4. **Run the Program:**
    ```bash
    python main.py
    ```

### Usage

1. The program starts listening for tasks. Type a task (e.g., "Open Notepad and type Hello").
2. The AI will process the screen state and decide the next best action based on the prompt.
3. Press **ESC** to stop the program at any time.

### Example Commands

```plaintext
> Open Notepad and type Hello
> Open Chrome and search cats
> Launch Calculator
```

## Future Enhancements

- Integrate with additional AI models to expand task handling capability.
- Extend platform compatibility for Linux and Mac.
- Add advanced gesture-based interactions for dynamic tasks.

## Contributing

Contributions are welcome! Feel free to fork the repo, submit PRs, or discuss ideas in the Issues tab.
