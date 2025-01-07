# Oromia Bank AI Assistant

This project is an AI assistant for Oromia Bank, capable of answering questions related to the bank, providing exchange rates, and more. The assistant is built using LangChain and OpenAI's GPT-4o model.

## Features

- Answer questions related to Oromia Bank.
- Provide exchange rates for various currencies.
- Multilingual support (Amharic, Oromo, English, and Tigrinya).
- Retrieve and index documents from the web and JSON files.

## Requirements

- Python 3.8+
- Docker (optional, for running in a container)

## Installation

### Running in Python

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/oromia-bank-ai-assistant.git
    cd oromia-bank-ai-assistant
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a `.env` file in the root directory and add the following:

    ```env
    OPENAI_API_KEY=your_openai_api_key
    ```

5. **Run the application:**

    ```bash
    python main.py
    ```

### Running in Docker

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/oromia-bank-ai-assistant.git
    cd oromia-bank-ai-assistant
    ```

2. **Build the Docker image:**

    ```bash
    docker build -t oromia-bank-ai-assistant .
    ```

3. **Run the Docker container:**

    ```bash
    docker run -d --name oromia-bank-ai-assistant -p 8000:8000 -e OPENAI_API_KEY=your_openai_api_key oromia-bank-ai-assistant
    ```

4. **Access the application:**

    Open your browser and go to `http://localhost:8000`.

## Usage

### Querying the Assistant

You can interact with the assistant by sending messages. The assistant can answer questions related to Oromia Bank, provide exchange rates, and more.

### Example Queries

- "What is the exchange rate of USD to ETB?"
- "Tell me about the history of Oromia Bank."
- "How can I open an account with Oromia Bank?"

## Project Structure

- `src/`: Contains the source code.
  - `controller/`: Contains the controller logic.
  - `model/`: Contains the data models.
  - `routes/`: Contains the API routes.
  - `utils/`: Contains utility functions and classes.
- `requirements.txt`: Lists the Python dependencies.
- `Dockerfile`: Contains the Docker configuration.
- `main.py`: The entry point of the application.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. 