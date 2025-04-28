# 💼 Tech Job Portal

![Demo](demo/video.gif)

**Tech Job Portal** is an intelligent job portal for the tech sector, using AI and semantic search to recommend the best job offers to each user.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Semantic Search**: Find relevant jobs using embeddings and cosine similarity.
- **AI-Powered Explanations**: Get AI-generated explanations about why each job is relevant to your query.
- **Modern Interface**: Built with Streamlit and custom CSS.
- **Easy Deployment**: Run the entire portal with a single command.

---

## Installation

Prerequisites:
- Python 3.10+
- pip

Clone the repository and install dependencies:

```bash
git clone https://github.com/juanludataanalyst/job_portal.git
cd job_portal
pip install -r requirements.txt
```

---

## Configuration

1. **Together AI API Key:**  
   Create a `.streamlit/secrets.toml` file with your key:

   ```toml
   [together]
   TOGETHER_API_KEY = "your_key_here"
   ```

2. **Job Data:**  
   Make sure you have the data files (`joined_data_standar.json`, `job_vectors.pkl`, etc.) in the root directory or in `data_joboffers/`.

---

## Usage

Run the application with:

```bash
streamlit run streamlit_app.py
```

Open your browser at `http://localhost:8501`.

---

## Project Structure

```
job_portal/
│
├── streamlit_app.py         # Main Streamlit app
├── data_loader.py           # Data and embeddings loader
├── generate_embeddings.py   # Job embeddings generation
├── prompts.py               # Prompts for AI explanations
├── requirements.txt         # Python dependencies
├── styles.css               # Custom styles
├── data_joboffers/          # Job data files
├── pages/                   # Other pages and utilities
└── ...
```

---

## Dependencies

Main libraries used (see [requirements.txt](https://github.com/juanludataanalyst/job_portal/blob/main/requirements.txt) for the full list):

- `streamlit`
- `sentence-transformers`
- `scikit-learn`
- `numpy`
- `together`
- `pandas`

---

## Environment Variables

- `TOGETHER_API_KEY`: Access key for Together AI LLM models (required for automatic explanations).

---

## Testing

There are currently no automated tests, but you can try the main flow by running:

```bash
streamlit run streamlit_app.py
```

And performing various searches in the interface.

---

## Contributing

Contributions are welcome!  
Open an issue or pull request to suggest improvements, report bugs, or propose new features.

---

## License

MIT
