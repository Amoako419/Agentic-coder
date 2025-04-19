# Agentic Coder

This project is an AI-powered coding assistant built using the Google Agent Development Kit (ADK). The assistant helps users debug and implement ideas seamlessly into their code.


## Project Structure

```
├── multi_tool_agent/ 
│   ├── agent.py          # Main agent implementation
│   ├── tools/            # Custom tools (if any)
├── adk/ 
│   ├── Lib/ 
│   │   ├── site-packages/ # Google ADK and dependencies
│   ├── Scripts/          # ADK CLI tools
├── .env                  # Environment variables
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Google ADK installed (`pip install google-adk`)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/amoako419/agentic-coder.git
   cd agentic-coder
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv adk
   source adk/Scripts/activate  # On Windows: adk\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Create a `.env` file in the root directory.
   - Add necessary API keys and configuration settings as key-value pairs.

5. Run the application:
   ```bash
   adk web
   ```

## Usage

Interact with the assistant through its conversational interface to search for products, compare prices, and get recommendations.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
