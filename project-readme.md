# HawkerGuru

An AI-powered assistant to help Singapore hawkers make informed decisions when bidding for hawker stalls.

## Project Structure

```
hawker_guru/
├── config/                    # Configuration files
│   ├── document_config.yaml   # Document processing configuration
│   └── .env                  # Environment variables
├── data/                     # All data files
│   ├── raw/                  # Original source files (e.g., Excel, GEOJSON)
│   ├── processed/            # Intermediate processed files
│   ├── current/             # Latest versions of processed documents
│   └── archive/             # Historical versions of processed files
├── src/                      # Source code
│   ├── data_processing/      # Data processing modules
│   │   ├── converters/      # Format conversion utilities
│   │   ├── processors/      # Document processing classes
│   │   └── managers/        # Data management utilities
│   ├── models/              # Data models and schemas
│   └── qa/                  # QA chain related code
├── tests/                    # Test files
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── pages/                   # Streamlit multipage app files
├── .streamlit/             # Streamlit configuration
├── HawkerGuru.py          # Main Streamlit application
└── requirements.txt       # Project dependencies
```

## Directory Descriptions

### Configuration (`config/`)
- `document_config.yaml`: Configuration for document processing
- `.env`: Environment variables (not tracked in Git)

### Data (`data/`)
- `raw/`: Original source files
  - Excel files
  - GEOJSON data
  - Text and Word documents
- `processed/`: Intermediate processed data
- `current/`: Latest versions of processed documents
- `archive/`: Historical versions for reference

### Source Code (`src/`)
- `data_processing/`: Core data processing functionality
  - `converters/`: File format conversion utilities
  - `processors/`: Document processing implementations
  - `managers/`: Data management and organization
- `models/`: Data models and type definitions
- `qa/`: Question-answering chain implementation

### Tests (`tests/`)
- `unit/`: Unit tests for individual components
- `integration/`: End-to-end integration tests

### Streamlit Application
- `pages/`: Additional pages for the Streamlit app
- `HawkerGuru.py`: Main application entry point

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`
4. Run the application:
   ```bash
   streamlit run HawkerGuru.py
   ```

## Development Guidelines

1. Data Processing:
   - Place new raw data files in `data/raw/`
   - Use appropriate processors in `src/data_processing/`
   - Store processed outputs in `data/processed/`

2. Testing:
   - Add unit tests in `tests/unit/`
   - Add integration tests in `tests/integration/`
   - Run tests before committing changes

3. Documentation:
   - Update README.md for significant changes
   - Document new features in relevant files
   - Keep docstrings up to date

## Note
This project was developed as part of the AI Champions Bootcamp 2024 (ABC2024).
