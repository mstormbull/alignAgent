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
├── main.py                 # Main application file
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── conversations/         # Directory for saved interview transcripts
│   ├── interview_2025-01-21_14-30-15.json
│   ├── interview_2025-01-21_15-45-22.json
│   └── ...
```

## Technical Architecture

### Core Components

1. **CompanyAlignmentFacilitator Class**: Main orchestrator handling all business logic
2. **LangChain Integration**: Uses ConversationChain for interviews and map-reduce summarization for reports
3. **Gradio Interface**: Modern web UI with tabbed interface for different workflows
4. **Data Persistence**: JSON-based storage of conversation transcripts

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

In `main.py`, you can modify:
- `max_turns`: Number of conversation turns per interview (default: 5)
- `temperature`: AI response creativity (default: 0.7)
- `chunk_size`: Document processing size for reports (default: 4000)

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

- API keys are loaded from environment variables (not hardcoded)
- Interview data is stored locally in JSON format
- No data is transmitted to external services beyond OpenAI API calls
- Consider implementing additional security measures for production use

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## License

This project is open source and available under the MIT License.
