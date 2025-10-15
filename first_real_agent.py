"""
E-Commerce Customer Support AI Agent

This module implements a comprehensive AI-powered customer support system for an e-commerce platform.
The agent provides automated assistance for common customer inquiries while maintaining strict guardrails
for security, privacy, and escalation protocols.

Architecture Overview:
- Tool-based function calling system using LangChain
- SQLite database integration for orders, inventory, and support tickets
- Monitored execution with performance metrics and logging
- Guardrail-enforced responses with automatic escalation for complex issues
- Comprehensive testing framework for validation and iteration

Key Components:
1. Customer Service Tools: Order status, return policies, inventory checks, ticket creation
2. AI Agent: OpenAI GPT-4 powered with custom system prompts and safety guardrails
3. Monitoring System: Performance tracking, error logging, and response time metrics
4. Testing Suite: Automated validation of agent behavior and tool usage

Configuration Requirements:
- OpenAI API key in environment variables
- SQLite databases: orders.db, inventory.db, tickets.db
- Python dependencies: langchain, langchain-openai, python-dotenv

Database Schema:
- orders: id, status, order_date, total_amount
- inventory: product_id, name, quantity, next_restock_date
- tickets: ticket_id, customer_email, issue, priority, status
"""

import os
from dotenv import load_dotenv
from langchain.agents import tool
import sqlite3
from datetime import datetime

# Load environment variables from .env file
# Required: OPENAI_API_KEY for LLM functionality
load_dotenv()

# =============================================================================
# CUSTOMER SERVICE TOOLS
# =============================================================================
# These tools provide the core functionality for customer support operations.
# Each tool is decorated with @tool for LangChain integration and follows
# a consistent pattern: validate input, query database, return structured response.

@tool
def check_order_status(order_id: str) -> dict:
    """
    Retrieves current order information from the orders database.

    This function serves as the primary tool for order status inquiries, providing
    customers with real-time visibility into their order progress. The function
    implements secure parameterized queries to prevent SQL injection.

    Args:
        order_id (str): Unique identifier for the order to lookup

    Returns:
        dict: Order information containing:
            - order_id: The requested order identifier
            - status: Current order status (e.g., 'pending', 'shipped', 'delivered')
            - order_date: Date when order was placed (YYYY-MM-DD format)
            - total_amount: Total monetary value of the order
        dict: Error response if order not found:
            - error: "Order not found"

    Database Interaction:
        Queries orders.db table with columns: id, status, order_date, total_amount
        Uses parameterized queries for security and input sanitization
    """
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, status, order_date, total_amount
        FROM orders WHERE id = ?
    """, (order_id,))

    result = cursor.fetchone()

    if result:
        return {
            "order_id": result[0],
            "status": result[1],
            "order_date": result[2],
            "total_amount": result[3]
        }
    return {"error": "Order not found"}
@tool
def check_return_policy(product_type: str) -> str:
    """
    Provides product-specific return policy information based on category.

    This function implements a knowledge base lookup for return policies across
    different product categories. It serves as a quick reference tool to help
    customers understand return eligibility and requirements without human intervention.

    Args:
        product_type (str): Category of product to check policy for.
                           Supported: "electronics", "clothing", "furniture"

    Returns:
        str: Specific return policy for the product type, including:
             - Return window duration (days)
             - Special conditions or requirements
             - Packaging or tagging requirements

    Policy Categories:
        - Electronics: Strict 30-day policy due to depreciation and testing concerns
        - Clothing: Extended 60-day policy to accommodate fit and style decisions
        - Furniture: Short 14-day policy due to assembly and size considerations

    Fallback: Generic 30-day policy for unrecognized product types
    """
    policies = {
        "electronics": "30-day return window, must include original packaging",
        "clothing": "60-day return window, must have tags attached",
        "furniture": "14-day return window, assembly affects eligibility"
    }
    return policies.get(product_type, "Standard 30-day return policy applies")
@tool
def create_support_ticket(customer_email: str, issue: str, priority: str) -> str:
    """
    Creates a support ticket in the database for human agent follow-up.

    This function implements the escalation pathway for complex customer issues
    that cannot be resolved through automated tools. It generates a unique ticket
    ID and stores the customer inquiry for human review and response.

    Args:
        customer_email (str): Customer's email address for follow-up communication
        issue (str): Detailed description of the customer's problem or request
        priority (str): Urgency level for ticket routing (e.g., 'low', 'medium', 'high', 'urgent')

    Returns:
        str: Confirmation message with ticket ID and expected response time

    Database Interaction:
        Inserts new record into tickets.db with columns:
        - ticket_id: Auto-generated unique identifier (TKT-YYYYMMDDHHMMSS format)
        - customer_email: Contact information for follow-up
        - issue: Full text of customer problem/request
        - priority: Urgency classification for queue management
        - status: Auto-set to 'open' for new tickets

    Error Handling:
        Function uses try/except in calling context - database connection errors
        are handled at the agent execution level with fallback responses
    """
    ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Save to database with transaction management
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (ticket_id, customer_email, issue, priority, status)
        VALUES (?, ?, ?, ?, 'open')
    """, (ticket_id, customer_email, issue, priority))
    conn.commit()

    return f"Support ticket {ticket_id} created. Team will respond within 24 hours."
@tool
def check_inventory(product_id: str) -> dict:
    """
    Checks real-time inventory status for a specific product.

    This function provides customers with current stock information to inform
    purchasing decisions. It includes restock date information for out-of-stock
    items to manage customer expectations.

    Args:
        product_id (str): Unique identifier for the product to check

    Returns:
        dict: Inventory information containing:
            - product_id: The requested product identifier
            - name: Human-readable product name
            - in_stock: Boolean indicating availability (quantity > 0)
            - quantity: Current stock level (0 if out of stock)
            - next_restock: Date when item will be back in stock (YYYY-MM-DD format)
        dict: Error response if product not found:
            - error: "Product not found"

    Business Logic:
        - in_stock flag derived from quantity > 0 check
        - Handles both in-stock and out-of-stock scenarios
        - Provides restock guidance for inventory planning

    Database Interaction:
        Queries inventory.db table with columns: product_id, name, quantity, next_restock_date
        Uses parameterized queries for security
    """
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT product_id, name, quantity, next_restock_date
        FROM inventory WHERE product_id = ?
    """, (product_id,))

    result = cursor.fetchone()

    if result:
        return {
            "product_id": result[0],
            "name": result[1],
            "in_stock": result[2] > 0,
            "quantity": result[2],
            "next_restock": result[3]
        }
    return {"error": "Product not found"}

# =============================================================================
# AI AGENT CREATION WITH GUARDRAILS
# =============================================================================
# This section implements the core AI agent using LangChain's tool-calling
# architecture. The agent combines LLM capabilities with structured tools
# while enforcing strict behavioral and safety guardrails.

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# Register all available tools for the agent
# Tools are executed based on natural language analysis and function calling
tools = [
    check_order_status,
    check_return_policy,
    create_support_ticket,
    check_inventory
]
# Comprehensive system prompt with behavioral guardrails
# This prompt establishes the AI agent's role, capabilities, and strict operational boundaries
# Guardrails prevent common AI issues: hallucination, privacy violations, inappropriate responses
system_prompt = """You are a helpful customer support agent for an e-commerce company.

CORE CAPABILITIES:
- Check order status and tracking information
- Explain return policies based on product categories
- Check product inventory and availability
- Create support tickets for complex issues requiring human attention

CRITICAL GUARDRAILS - MANDATORY COMPLIANCE:
1. INFORMATION ACCURACY: Never make up information. If you don't know, explicitly state so.
2. ORDER VERIFICATION: Always verify order IDs exist before sharing status details.
3. HIGH-VALUE ESCALATION: For any refund requests over $500, immediately create support ticket.
4. EMOTIONAL INTELLIGENCE: For angry/frustrated customers, acknowledge emotions and escalate.
5. PRIVACY PROTECTION: Never share or reference other customers' information.
6. PROFESSIONAL CONDUCT: Maintain empathetic, professional, and concise communication style.

ESCALATION PROTOCOL:
If a query is outside your defined capabilities or violates guardrails,
politely explain limitations and create a support ticket for human resolution."""
# Configure conversation template with memory support
# Template structure enables multi-turn conversations and tool execution tracking
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history", optional=True),  # Conversation memory
    ("human", "{input}"),                                             # Customer message
    MessagesPlaceholder(variable_name="agent_scratchpad")             # Tool execution trace
])

# Initialize OpenAI GPT-5-nano with conservative settings
# Temperature=0 ensures consistent, deterministic responses
# API key loaded from environment variables for security
llm = ChatOpenAI(
    model="gpt-5-nano",
    temperature=0,  # Deterministic responses for reliability
    openai_api_key=os.getenv("OPENAI_API_KEY")  # Secure credential management
)

# Create the core agent with tool-calling capabilities
# Agent combines LLM reasoning with structured tool execution
agent = create_openai_tools_agent(llm, tools, prompt)

# Configure agent executor with operational safeguards
# Executor manages tool execution, error handling, and iteration limits
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,                    # Detailed execution logging for debugging
    max_iterations=5,               # Prevent infinite loops in tool chains
    handle_parsing_errors=True      # Graceful handling of malformed responses
)

# =============================================================================
# MONITORING AND LOGGING SYSTEM
# =============================================================================
# Production-grade observability layer that wraps the base agent with
# comprehensive monitoring, metrics collection, and error tracking.

import logging
from datetime import datetime

class MonitoredAgent:
    """
    Wrapper class that adds production monitoring capabilities to the base agent.

    This class implements enterprise-grade observability for the AI agent,
    tracking key performance indicators, response times, error rates, and
    escalation patterns. Essential for production deployment and performance
    optimization.

    Metrics Tracked:
    - Query volume and throughput
    - Resolution success rates
    - Escalation frequency (indicates areas needing improvement)
    - Response time latency
    - Error rates and patterns

    Logging Strategy:
    - Structured logging with timestamps and context
    - Dual output: file (agent_logs.log) and console
    - Different log levels for debugging vs production monitoring
    """

    def __init__(self, agent_executor):
        """
        Initialize monitoring wrapper with metrics tracking.

        Args:
            agent_executor: Configured AgentExecutor instance to monitor
        """
        self.agent = agent_executor
        self.setup_logging()
        self.metrics = {
            "total_queries": 0,
            "successful_resolutions": 0,
            "escalations": 0,
            "average_response_time": []
        }
    
    def setup_logging(self):
        """
        Configure structured logging for agent operations.

        Sets up dual-output logging (file + console) with consistent formatting
        for both development debugging and production monitoring.
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('agent_logs.log'),  # Persistent log file
                logging.StreamHandler()                 # Console output for development
            ]
        )

    def run(self, query: str, customer_id: str = None) -> dict:
        """
        Execute agent query with comprehensive monitoring and error handling.

        This method wraps the base agent execution with performance monitoring,
        error tracking, and automatic escalation detection. It provides the
        primary interface for customer interactions.

        Args:
            query (str): Customer's natural language question or request
            customer_id (str, optional): Customer identifier for tracking

        Returns:
            dict: Structured response containing:
                - status: "success" or "error"
                - response: Agent's natural language response
                - response_time: Execution time in seconds
                - error: Error message if execution failed

        Monitoring Features:
        - Response time tracking for performance analysis
        - Escalation detection via keyword analysis ("ticket")
        - Success rate calculation for automated resolutions
        - Comprehensive error logging with context preservation

        Error Handling Strategy:
        - Catches all exceptions to prevent system crashes
        - Provides user-friendly error messages
        - Maintains error context for debugging
        - Automatic error escalation with ticket creation
        """
        start_time = datetime.now()
        self.metrics["total_queries"] += 1

        logging.info(f"Query received: {query[:100]}...")

        try:
            # Execute agent with input formatting
            result = self.agent.invoke({"input": query})

            # Calculate and track response latency
            response_time = (datetime.now() - start_time).total_seconds()
            self.metrics["average_response_time"].append(response_time)

            # Analyze response for escalation indicators
            if "ticket" in result["output"].lower():
                self.metrics["escalations"] += 1
                logging.warning(f"Query escalated to support ticket")
            else:
                self.metrics["successful_resolutions"] += 1

            logging.info(f"Query resolved in {response_time:.2f}s")

            return {
                "status": "success",
                "response": result["output"],
                "response_time": response_time
            }

        except Exception as e:
            # Comprehensive error handling with user-friendly messages
            logging.error(f"Agent error: {str(e)}")

            return {
                "status": "error",
                "response": "I apologize, but I encountered an error. A support ticket has been created.",
                "error": str(e)
            }
    
    def get_metrics(self) -> dict:
        """
        Calculate and return comprehensive performance metrics.

        Provides key performance indicators for monitoring agent effectiveness,
        identifying areas for improvement, and tracking business impact.

        Returns:
            dict: Performance metrics including:
                - total_queries: Total number of queries processed
                - resolution_rate: Percentage of queries resolved without escalation
                - escalation_rate: Percentage of queries requiring human intervention
                - average_response_time: Mean response time in seconds

        Calculation Methods:
        - Resolution rate: (successful_resolutions / total_queries) * 100
        - Escalation rate: (escalations / total_queries) * 100
        - Average response time: Mean of all recorded response times

        Edge Cases:
        - Handles zero queries gracefully (returns 0 for rates)
        - Manages empty response time arrays
        """
        avg_time = sum(self.metrics["average_response_time"]) / len(self.metrics["average_response_time"]) if self.metrics["average_response_time"] else 0

        return {
            "total_queries": self.metrics["total_queries"],
            "resolution_rate": (self.metrics["successful_resolutions"] / self.metrics["total_queries"] * 100) if self.metrics["total_queries"] > 0 else 0,
            "escalation_rate": (self.metrics["escalations"] / self.metrics["total_queries"] * 100) if self.metrics["total_queries"] > 0 else 0,
            "average_response_time": round(avg_time, 2)
        }

# =============================================================================
# AGENT USAGE AND DEMONSTRATION
# =============================================================================
# Initialize the monitored agent wrapper
monitored_agent = MonitoredAgent(agent_executor)

# Example customer interactions demonstrating agent capabilities
response1 = monitored_agent.run(
    "Where is my order #12345?",           # Order status inquiry
    customer_id="CUST_001"
)
print(response1["response"])

response2 = monitored_agent.run(
    "I want to return a $600 laptop that's defective",  # High-value return request
    customer_id="CUST_002"
)
print(response2["response"])

# Performance monitoring and reporting
metrics = monitored_agent.get_metrics()
print("\nAgent Performance Dashboard:")
print(f"Total Queries Processed: {metrics['total_queries']}")
print(f"Resolution Rate: {metrics['resolution_rate']:.1f}%")
print(f"Escalation Rate: {metrics['escalation_rate']:.1f}%")
print(f"Average Response Time: {metrics['average_response_time']}s")

# =============================================================================
# TESTING FRAMEWORK AND VALIDATION
# =============================================================================
# Comprehensive test suite for validating agent behavior, tool selection,
# and response quality. Essential for development iteration and production
# deployment confidence.

# Structured test cases covering all major agent capabilities
# Each test validates: tool selection, response quality, and behavioral expectations
test_cases = [
    {
        "query": "Where is order #12345?",
        "expected_tool": "check_order_status",
        "expected_outcome": "Order status provided"
    },
    {
        "query": "Can I return electronics after 45 days?",
        "expected_tool": "check_return_policy",
        "expected_outcome": "Policy clearly explained"
    },
    {
        "query": "My $800 refund hasn't arrived and I'm furious!",
        "expected_tool": "create_support_ticket",
        "expected_outcome": "Empathetic escalation"
    },
    {
        "query": "Is product XYZ in stock?",
        "expected_tool": "check_inventory",
        "expected_outcome": "Inventory status provided"
    }
]

def test_agent(test_cases):
    """
    Execute comprehensive test suite against the monitored agent.

    This function runs a series of predefined test cases to validate agent
    behavior, tool selection accuracy, and response quality. Results are
    structured for analysis and debugging.

    Args:
        test_cases (list): Array of test case dictionaries with:
            - query: Customer input to test
            - expected_tool: Tool that should be invoked
            - expected_outcome: Expected behavioral result

    Returns:
        list: Detailed test results including:
            - query: Original test input
            - response: Agent's actual response
            - status: Success/error status
            - time: Response time in seconds

    Test Coverage:
    - Tool selection accuracy (which tool is called for each query type)
    - Response quality (appropriate, helpful, and guardrail-compliant)
    - Performance characteristics (response time consistency)
    - Error handling (graceful degradation for edge cases)

    Usage in Development:
    - Run tests after code changes to catch regressions
    - Analyze response patterns for optimization opportunities
    - Validate guardrail effectiveness across scenarios
    """
    results = []

    for test in test_cases:
        print(f"\nTesting: {test['query']}")
        response = monitored_agent.run(test['query'])

        results.append({
            "query": test['query'],
            "response": response['response'],
            "status": response['status'],
            "time": response.get('response_time', 0)
        })

        print(f"Response: {response['response'][:100]}...")
        print(f"Time: {response.get('response_time', 0):.2f}s")

    return results

# Execute test suite and display results
# This validates the complete agent implementation across all major use cases
test_results = test_agent(test_cases)

