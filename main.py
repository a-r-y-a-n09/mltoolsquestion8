from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import re
import json

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function definitions for parameter extraction
FUNCTION_PATTERNS = [
    # report_office_issue - Pattern 1: "issue_code reported in/for department"
    {
        "pattern": r"^(\d+)\s+reported\s+(?:in|for|to)\s+(?:the\s+)?(.+?)(?:\s+department)?$",
        "name": "report_office_issue",
        "params": ["issue_code", "department"],
        "types": [int, str]
    },
    # report_office_issue - Pattern 2: "Report office issue ..."
    {
        "pattern": r"report\s+office\s+issue\s+(\d+)\s+(?:for|in|to)\s+(?:the\s+)?(.+?)(?:\s+department)?$",
        "name": "report_office_issue",
        "params": ["issue_code", "department"],
        "types": [int, str]
    },
    # get_ticket_status
    {
        "pattern": r"what\s+is\s+(?:the\s+)?status\s+of\s+ticket\s+(\d+)",
        "name": "get_ticket_status",
        "params": ["ticket_id"],
        "types": [int]
    },
    # schedule_meeting
    {
        "pattern": r"schedule\s+(?:a\s+)?meeting\s+on\s+([\d-]+)\s+at\s+([\d:]+)\s+in\s+(.+?)$",
        "name": "schedule_meeting",
        "params": ["date", "time", "meeting_room"],
        "types": [str, str, str]
    },
    # get_expense_balance
    {
        "pattern": r"show\s+(?:my\s+)?expense\s+balance\s+for\s+employee\s+(\d+)",
        "name": "get_expense_balance",
        "params": ["employee_id"],
        "types": [int]
    },
    # calculate_performance_bonus
    {
        "pattern": r"calculate\s+performance\s+bonus\s+for\s+employee\s+(\d+)\s+for\s+(\d{4})",
        "name": "calculate_performance_bonus",
        "params": ["employee_id", "current_year"],
        "types": [int, int]
    }
]

def parse_query(q: str):
    """Parse the query string and extract function name and arguments."""
    q_lower = q.lower().strip()
    
    for func_def in FUNCTION_PATTERNS:
        match = re.search(func_def["pattern"], q_lower, re.IGNORECASE)
        if match:
            groups = match.groups()
            arguments = {}
            
            for i, param_name in enumerate(func_def["params"]):
                value = groups[i]
                param_type = func_def["types"][i]
                
                if param_type == int:
                    arguments[param_name] = int(value)
                else:
                    # Clean up the value
                    value = value.strip()
                    # Keep department names as uppercase if they're acronyms
                    if param_name == "department":
                        value = value.upper()
                    arguments[param_name] = value
            
            return {
                "name": func_def["name"],
                "arguments": json.dumps(arguments, separators=(',', ': '))
            }
    
    return {
        "name": "unknown_function",
        "arguments": json.dumps({"query": q}, separators=(',', ': '))
    }

@app.get("/execute")
async def execute(q: str = Query(..., description="Query string containing the question")):
    """
    Endpoint to parse query and return function name and arguments.
    
    Example: /execute?q=What is the status of ticket 83742?
    Returns: {"name": "get_ticket_status", "arguments": "{\"ticket_id\": 83742}"}
    """
    result = parse_query(q)
    return result

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "TechNova Corp FastAPI Function Router",
        "endpoint": "/execute?q=<your_query>",
        "examples": [
            "/execute?q=What is the status of ticket 83742?",
            "/execute?q=Schedule a meeting on 2025-02-15 at 14:00 in Room A",
            "/execute?q=Show my expense balance for employee 10056",
            "/execute?q=Calculate performance bonus for employee 10056 for 2025",
            "/execute?q=Report office issue 45321 for the Facilities department",
            "/execute?q=15801 reported in IT department"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)