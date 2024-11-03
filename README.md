# KLEO Backend

KLEO Backend is a FastAPI application that serves as the backend for the KLEO project.

## Table of Contents

- [KLEO Backend](#kleo-backend)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/kleo-backend.git
cd kleo-backend
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables for MongoDB connection:

- We have given `.env.example` file. Just copy that and rename it to `.env` and replace the variables inside with appropriate values.

## Usage

To start the FastAPI application, run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You can now access the API at http://127.0.0.1:8000.

Also you can checkout Swagger documentation at http://127.0.0.1:8000/docs.
