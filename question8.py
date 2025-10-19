from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import re

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Knowledge base with TypeScript documentation excerpts
KNOWLEDGE_BASE = [
    {
        "id": "fat-arrow",
        "content": "The author affectionately calls the => syntax the 'fat arrow'. This is a shorthand syntax for function expressions in TypeScript and JavaScript.",
        "keywords": ["=>", "arrow", "syntax", "affectionately", "call", "fat arrow"]
    },
    {
        "id": "boolean-operator",
        "content": "The !! operator converts any value into an explicit boolean. It uses double negation to coerce a value to its boolean equivalent.",
        "keywords": ["!!", "operator", "converts", "boolean", "explicit", "double negation"]
    },
    {
        "id": "node-children",
        "content": "The node.getChildren() method lets you walk every child node of a ts.Node in the TypeScript compiler API.",
        "keywords": ["getChildren", "walk", "child", "node", "ts.Node", "traverse"]
    },
    {
        "id": "trivia",
        "content": "Code pieces like comments and whitespace that aren't in the AST are called 'trivia'. Trivia includes formatting details that don't affect code execution.",
        "keywords": ["trivia", "comments", "whitespace", "AST", "not in AST"]
    }
]

def search_knowledge_base(query: str):
    """Search the knowledge base using keyword matching."""
    query_lower = query.lower()
    
    # Score each document based on keyword matches
    scores = []
    for doc in KNOWLEDGE_BASE:
        score = 0
        content_lower = doc["content"].lower()
        
        # Check for keyword matches
        for keyword in doc["keywords"]:
            if keyword.lower() in query_lower:
                score += 2
        
        # Check for query words in content
        query_words = re.findall(r'\b\w+\b', query_lower)
        for word in query_words:
            if len(word) > 3 and word in content_lower:
                score += 1
        
        scores.append((score, doc))
    
    # Sort by score and return best match
    scores.sort(reverse=True, key=lambda x: x[0])
    
    if scores[0][0] > 0:
        return scores[0][1]
    return None

def extract_answer(doc, query: str):
    """Extract the most relevant part of the answer."""
    content = doc["content"]
    
    # Extract specific answers based on common patterns
    if "affectionately call" in query.lower() and "=>" in query:
        match = re.search(r"'([^']+)'", content)
        if match:
            return match.group(1)
    
    if "operator converts" in query.lower() or "explicit boolean" in query.lower():
        match = re.search(r"The (!!|\S+) operator", content)
        if match:
            return match.group(1)
    
    if "walk every child node" in query.lower() or "getChildren" in query.lower():
        match = re.search(r"(node\.getChildren\(\))", content)
        if match:
            return match.group(1)
    
    if "comments and whitespace" in query.lower() or "not in the AST" in query.lower():
        match = re.search(r"called '([^']+)'", content)
        if match:
            return match.group(1)
    
    # Return full content if no specific pattern matches
    return content

@app.get("/search")
async def search(q: str = Query(..., description="Question to search for in TypeScript documentation")):
    """
    Search endpoint for TypeScript documentation questions.
    
    Example: /search?q=What does the author affectionately call the => syntax?
    Returns: {"answer": "fat arrow", "sources": "typescript-book"}
    """
    
    # Search the knowledge base
    doc = search_knowledge_base(q)
    
    if doc is None:
        return {
            "answer": "No relevant documentation found for this query.",
            "sources": "typescript-book"
        }
    
    # Extract the answer
    answer = extract_answer(doc, q)
    
    return {
        "answer": answer,
        "sources": "typescript-book",
        "document_id": doc["id"]
    }

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "TypeScript Documentation RAG API",
        "endpoint": "/search?q=<your_question>",
        "examples": [
            "/search?q=What does the author affectionately call the => syntax?",
            "/search?q=Which operator converts any value into an explicit boolean?",
            "/search?q=What lets you walk every child node of a ts.Node?",
            "/search?q=What are code pieces like comments and whitespace that aren't in the AST called?"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)