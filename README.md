# Smart Meeting Assistant MCP Server

A comprehensive Model Context Protocol (MCP) server that provides intelligent meeting scheduling and calendar management with AI-powered features.

## Features

### 🤖 AI-Powered Scheduling
- **Intelligent Conflict Detection**: Automatically detects and prevents scheduling conflicts
- **Optimal Time Slot Recommendations**: Uses AI to suggest the best meeting times based on participant availability and preferences
- **Smart Agenda Generation**: Automatically generates relevant meeting agendas based on meeting type and participants

### 📊 Meeting Analytics
- **Meeting Pattern Analysis**: Analyzes meeting frequency, duration, and productivity trends
- **Effectiveness Scoring**: Evaluates meeting effectiveness and provides improvement suggestions
- **Workload Balancing**: Monitors and balances meeting load across team members

### 🔧 Advanced Features
- **Multi-timezone Support**: Handles participants across different time zones
- **Schedule Optimization**: Provides personalized schedule optimization recommendations
- **Focus Time Protection**: Identifies and protects focus blocks in schedules

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd smart-meeting-assistant-mcp
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the server:**
```bash
python src/server.py
```

## MCP Tools

### 1. `create_meeting`
Schedule a new meeting with automatic conflict detection.

**Parameters:**
- `title` (string): Meeting title
- `participants` (array): List of participant IDs
- `duration` (integer): Meeting duration in minutes
- `start_time` (datetime): Meeting start time
- `preferences` (object, optional): Meeting preferences

**Example:**
```json
{
  "title": "Sprint Planning",
  "participants": ["user_1", "user_2", "user_3"],
  "duration": 60,
  "start_time": "2024-12-10T14:00:00Z"
}
```

### 2. `find_optimal_slots`
Find optimal meeting time slots using AI recommendations.

**Parameters:**
- `participants` (array): List of participant IDs
- `duration` (integer): Meeting duration in minutes
- `start_date` (date): Search start date
- `end_date` (date): Search end date

**Returns:**
- List of optimal time slots ranked by quality score
- Recommendation reasons for each slot

### 3. `detect_scheduling_conflicts`
Detect scheduling conflicts for a user within a time range.

**Parameters:**
- `user_id` (string): User ID to check
- `start_time` (datetime): Start time for conflict check
- `end_time` (datetime): End time for conflict check

**Returns:**
- List of conflicts with severity levels
- Conflict types: overlap, back-to-back, excessive meetings

### 4. `analyze_meeting_patterns`
Analyze meeting patterns and behavior for a user.

**Parameters:**
- `user_id` (string): User ID to analyze
- `period` (string): Analysis period (week, month, quarter)

**Returns:**
- Meeting statistics and trends
- Effectiveness analysis
- Personalized recommendations

### 5. `generate_agenda_suggestions`
Generate smart agenda suggestions based on meeting context.

**Parameters:**
- `meeting_topic` (string): Meeting topic or title
- `participants` (array): List of participant IDs

**Returns:**
- Customized agenda items
- Meeting type detection
- Participant-specific considerations

### 6. `calculate_workload_balance`
Calculate meeting workload balance across team members.

**Parameters:**
- `team_members` (array): List of team member IDs

**Returns:**
- Individual workload statistics
- Team balance analysis
- Redistribution recommendations

### 7. `score_meeting_effectiveness`
Score meeting effectiveness and provide improvement suggestions.

**Parameters:**
- `meeting_id` (string): Meeting ID to score

**Returns:**
- Effectiveness score (1-5 scale)
- Score breakdown by factors
- Specific improvement suggestions

### 8. `optimize_meeting_schedule`
Provide schedule optimization recommendations.

**Parameters:**
- `user_id` (string): User ID to optimize

**Returns:**
- Optimization recommendations
- Priority levels
- Expected impact metrics

## Sample Data

The server comes pre-loaded with:
- **5 users** across different time zones (New York, London, Tokyo, Los Angeles, Sydney)
- **70+ sample meetings** with realistic distribution
- **Meeting templates** for different meeting types
- **User preferences** and work hour configurations

## Meeting Types

The system recognizes and handles various meeting types:
- **Standup**: Daily team synchronization
- **Review**: Project and sprint reviews
- **Planning**: Strategic and sprint planning sessions
- **Brainstorm**: Creative and problem-solving sessions
- **One-on-One**: Individual meetings
- **Presentation**: Demos and client presentations
- **Training**: Learning and knowledge transfer sessions

## AI Features

### Smart Scheduling Algorithm
The system uses a sophisticated scoring algorithm that considers:
- Participant work hours and time zones
- Meeting preferences and blocked times
- Historical meeting patterns
- Optimal meeting times (mid-morning, early afternoon)
- Meeting load balancing

### Effectiveness Scoring
Meetings are scored based on:
- **Duration optimization**: Sweet spot of 30-45 minutes
- **Participant count**: Optimal range of 3-6 people
- **Agenda quality**: Presence of structured agenda
- **Meeting type appropriateness**: Duration matching meeting type

### Pattern Analysis
The system analyzes:
- Meeting frequency and distribution
- Focus time availability
- Meeting clustering patterns
- Workload balance across team members

## Configuration

### User Preferences
Each user can configure:
- Work hours by day of week
- Maximum meetings per day
- Preferred meeting lengths
- No-meeting time blocks
- Time zone settings

## Use Cases

### For Teams
- **Daily standups**: Optimize recurring meeting schedules
- **Sprint planning**: Find optimal times for cross-timezone teams
- **Review meetings**: Balance workload and improve effectiveness

