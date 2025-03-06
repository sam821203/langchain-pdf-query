# PDF Query App with LangChain, Python, and Vue.js

PDF Query App with LangChain, Python, and Vue.js. This application enables users to query PDF documents using natural language.

## Features

1. **PDF Upload and Parsing**
2. **Text Embedding and Retrieval (RAG)**
3. **Vector Data Storage with Chroma**
4. **OpenAI API Integration**
5. **Interactive Vue.js**

## Getting Started

### Prerequisites

- Python 3.10 or later
- Node.js 16 or later

### Installation

1. Clone the repository:

   ```bash
   <!-- Replace YOUR_REPO_URL with your GitHub repository URL -->
   git clone https://github.com/...
   cd pdf-query-app
   ```

2. Install Backend Dependencies:

   ```bash
   poetry install --no-root
   ```

3. Set up your environment variables:

   - Rename the `.env.example` file to `.env` and update the variables inside with your own values. Example:

   ```bash
   mv .env.example .env
   ```

   - Example .env file:

   ```bash
   OPENAI_API_KEY=your_api_key
   ```

4. Install Frontend Dependencies:

   ```bash
   cd ../frontend
   npm install
   ```

## Running the App

1. Start Backend Service

   ```bash
   cd backend
   python main.py
   ```

2. Start Frontend Service

   ```bash
   cd frontend
   npm run dev
   ```

## FAQ

**Q: How do I set environment variables?**  
A: Rename .env.example to .env and fill in the required API keys.

**Q: Why is my query not returning results?**  
A: Ensure your OpenAI API Key is correct.

**Q: Can I contribute?**  
A: Yes! Feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
