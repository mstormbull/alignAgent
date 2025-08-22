# Company Alignment Facilitator

An AI-powered application for conducting alignment interviews with team members and generating comprehensive reports to identify organizational alignment, consensus areas, and potential misalignments.

## Features

- **Session Management**: Admin interface to set alignment topics and manage interview sessions
- **AI Interviewer**: Stateful conversational agent that conducts professional, neutral interviews
- **Data Capture**: Automatic saving of interview transcripts as JSON files
- **Report Generation**: AI-powered synthesis of all interviews using LangChain's map-reduce summarization
- **Modern UI**: Clean, intuitive Gradio interface with tabbed workflows

## Prerequisites

- Python 3.8 or higher
- OpenAI API key with access to GPT-4 models

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```
   
   Or create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

## Usage

### Starting the Application

Run the main application:
```bash
python main.py
```

The application will start a local web server (typically at `http://localhost:7860`).

### Workflow

#### 1. Admin Setup (Tab 1: Admin & Reporting)
- Enter an alignment topic (e.g., "Our Q4 strategic priorities")
- Click "Start New Alignment Session"
- The interview interface will be activated

#### 2. Conduct Interviews (Tab 2: Employee Interview)
- Employees can now interact with the AI interviewer
- Each interview consists of 5 conversational turns
- The AI asks open-ended, follow-up questions based on responses
- Interviews are automatically saved when completed

#### 3. Generate Reports (Tab 1: Admin & Reporting)
- After conducting multiple interviews, click "Generate Alignment Report"
- The system will analyze all interview transcripts
- A comprehensive report will be generated identifying:
  - Key recurring themes
  - Areas of consensus
  - Potential misalignments
  - Actionable recommendations

### File Structure

```
alignAgent-1/
├── main.py                 # Application entry point
├── config.py              # Configuration management
├── models.py              # Data structures and types
├── ai_interviewer.py      # AI conversation logic
├── data_manager.py        # Data persistence
├── report_generator.py    # Report generation
├── facilitator.py         # Main orchestrator
├── ui_interface.py        # User interface
├── tests.py              # Unit tests
├── example_usage.py      # Usage examples
├── setup.py              # Setup script
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── conversations/       # Directory for saved interview transcripts
│   ├── interview_2025-01-21_14-30-15.json
│   ├── interview_2025-01-21_15-45-22.json
│   └── ...
```

## Technical Architecture

### Modular Design

The application follows a clean, modular architecture with clear separation of concerns:

1. **`config.py`**: Centralized configuration management
2. **`models.py`**: Data structures and type definitions
3. **`ai_interviewer.py`**: AI conversation logic and interview management
4. **`data_manager.py`**: File operations and data persistence
5. **`report_generator.py`**: AI-powered analysis and report generation
6. **`facilitator.py`**: Main orchestrator coordinating all components
7. **`ui_interface.py`**: Gradio user interface management
8. **`main.py`**: Application entry point

### Core Components

1. **CompanyAlignmentFacilitator**: Main orchestrator handling all business logic
2. **AIInterviewer**: Stateful conversational AI using LangChain
3. **DataManager**: File operations and conversation storage
4. **ReportGenerator**: AI-powered analysis using map-reduce summarization
5. **UIManager**: Modern Gradio interface with tabbed workflows

### AI Interviewer Behavior

The AI interviewer is designed to:
- Act as a neutral, professional researcher
- Ask open-ended questions that encourage deeper thinking
- Avoid leading or judgmental responses
- Probe for details when responses are brief
- Maintain conversation context throughout the interview

### Report Generation

The report generation uses LangChain's map-reduce strategy:
1. **Map**: Each interview transcript is processed individually
2. **Reduce**: All processed summaries are combined into a final comprehensive report
3. **Output**: Structured report with executive summary, insights, and recommendations

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required OpenAI API key for GPT-4 access

### Customization Options

In `config.py`, you can modify:
- `MAX_INTERVIEW_TURNS`: Number of conversation turns per interview (default: 5)
- `OPENAI_TEMPERATURE`: AI response creativity (default: 0.7)
- `CHUNK_SIZE`: Document processing size for reports (default: 4000)
- `OPENAI_MODEL`: LLM model to use (default: "gpt-4-turbo-preview")

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY environment variable is required"**
   - Ensure you've set the environment variable correctly
   - Check that your API key is valid and has sufficient credits

2. **"No interview transcripts found"**
   - Make sure you've conducted at least one interview
   - Check that the `conversations/` directory exists and contains JSON files

3. **Interview interface not working**
   - Ensure an admin has started an alignment session
   - Check that the session is still active

### Logging

The application includes comprehensive logging. Check the console output for detailed information about:
- Session starts/stops
- Interview progress
- File save operations
- Error messages

## Security Considerations

### API Key Security
- **Environment Variables**: API keys are loaded from environment variables (not hardcoded)
- **No Hardcoded Secrets**: No private keys, passwords, or credentials are stored in the code
- **Secure Storage**: Use environment variables or `.env` files (never commit these to version control)

### Data Security
- **Local Storage**: Interview data is stored locally in JSON format
- **No External Transmission**: No data is transmitted to external services beyond OpenAI API calls
- **File Permissions**: Ensure proper file permissions on the `conversations/` directory

### Best Practices
- **Git Ignore**: The `.gitignore` file prevents accidental commit of sensitive files
- **Environment Files**: Never commit `.env` files or files containing API keys
- **Production Security**: Consider implementing additional security measures for production use
- **API Key Rotation**: Regularly rotate your OpenAI API keys
- **Access Control**: Restrict access to the application and data files

### Security Checklist
- [ ] API key stored in environment variable
- [ ] No hardcoded credentials in code
- [ ] `.env` file added to `.gitignore`
- [ ] Proper file permissions set
- [ ] Regular API key rotation
- [ ] Secure deployment practices

## Development

### Running Tests

The application includes comprehensive unit tests:

```bash
python tests.py
```

### Security Validation

Run the security check to ensure no sensitive data is exposed:

```bash
python security_check.py
```

This will verify:
- No hardcoded credentials
- Proper environment variable usage
- No sensitive files present
- Correct .gitignore configuration
- Secure file permissions

### Code Structure

The modular design makes it easy to:
- **Test individual components** in isolation
- **Extend functionality** by adding new modules
- **Maintain code** with clear separation of concerns
- **Debug issues** with focused component testing

### Adding New Features

1. **Data Models**: Add new models in `models.py`
2. **Business Logic**: Extend appropriate modules (`ai_interviewer.py`, `report_generator.py`, etc.)
3. **UI Components**: Add new interface elements in `ui_interface.py`
4. **Configuration**: Add new settings in `config.py`

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## License

This project is open source and available under the MIT License.
