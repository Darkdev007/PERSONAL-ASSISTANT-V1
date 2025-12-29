import os
from datetime import datetime
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from calendar_logic import create_calendar_event
from email_logic import send_email
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()
api_key =  os.getenv("OPENAI_API_KEY")

model = init_chat_model("gpt-4.1", api_key=api_key)

@tool
def calendar_event(title:str, start_time:str, end_time:str, location: str = "")-> str:
    """Create a calender event. Requires exact ISO Datetime foramt."""
    response = create_calendar_event(title, start_time, end_time)
    return response

@tool
def email(
    to: str,
    subject:str,
    body_text: str,
)-> str:
    """Send an email via email API. Requires properly formatted addreeses."""
    response = send_email(to, subject, body_text)
    return response


#For the future
# @tool
# def get_available_time_slots(
#     date:str, #ISO format
#     duration_minutes : int
# )

#SUB AGENTS
from langchain.agents import create_agent

current_datetime = datetime.now()
iso_format_str = current_datetime.isoformat()

CALENDAR_AGENT_PROMPT = (
    "You are a calendar scheduling assistant."
    f"The current date of the day is giving to you in the {iso_format_str} variable use it to schedule properly e.g if the date is 2025-12-7 an event a week from now will be 2025-12-14"
    "Parse natural language scheduling resuests(e.g., 'next Tuesday at 2pm')"
    "into proper ISO datetime formats. "
    "Use calender_event to schedule events. "
    "Always confirm what was scheduled in your final response. " 
)

calendar_agent = create_agent(
    model,
    tools=[calendar_event],
    system_prompt=CALENDAR_AGENT_PROMPT,
    # middleware = [HumanInTheLoopMiddleware(
    #     interrupt_on={"calendar_event" : True},
    #     description_prefix= "Calendar event pending approval"
    # )]
)

# query = "Schedule a meeting for next week thursday 2pm"
# for step in calendar_agent.stream(
#     {"messages":[{"role": "user", "content": query}]}
# ):
#     for update in step.values():
#         for message in update.get("messages",[]):
#             message.pretty_print()

#CREATE AND EMAIL AGENT
EMAIL_AGENT_PROMPT = (
    "You are an email assistant."
    "Compose the body of the emails based on natural language requests. "
    "Extract recipient information and craft appropriate subject lines and body text."
    "Use email to send the message. " 
    "Always confirm what was sent in your final response."
    
)
email_agent = create_agent(
    model,
    tools=[email],
    system_prompt=EMAIL_AGENT_PROMPT,
    # middleware=[HumanInTheLoopMiddleware(
    #     interrupt_on={"email" : True},
    #     description_prefix="Outbound email pending approval"
    #)
#]
)

# query = "Send an email to my father thanking him for being there for me and always supporting me. His email is whymfa@gmail.com"

# for step in email_agent.stream(
#     {"messages": [{"role" : "user", "content": query,
#                     }]}
# ):
#     for update in step.values():
#         for message in update.get("messages", []):
#             message.pretty_print()

#WRAP SUB_AGENTS AS TOOLS
@tool
def schedule_event(request: str) -> str:
    """Schedule calendar events using natural language.
    
    Use this when the user wants to create, modify, or check calendar appointments.
    Handles date/time parsing, availability checking, and event creation.

    Input:  Natural language scheduling request(e.g, 'meeting with the design team next Teusday as 2pm')
    """
    result = calendar_agent.invoke({
        "messages": [{"role":"user", "content": request}]
    })
    return result["messages"][-1].text

@tool 
def manage_email(request: str) -> str:
    """Send emails using natural language.

    Use this when the user wants to send notifications, reminders or any email
    communication. Handles recipient extraction, subject generation , and email 
    composition.

    Input: Natural language email request (e.g., 'send them a reminder about
    the meeting') 
    
    """
    result = email_agent.invoke(
        {
            "messages" : [{"role": "user", "content" : request}]
        }
    )
    return result["messages"][-1].text

#CREATE THE SUPERVISOR AGENT
SUPERVISOR_PROMPT = (
    "You are a helpful personal assistanrt. "
    "You can schedule calendar events and send emails. "
    "Break down user requests into appropriate tool calls and coordinate the results. "
    "When a request involves multiple actions, use multiple tools in sequence." 
)

supervisor_agent = create_agent(
    model,
    tools = [schedule_event, manage_email],
    system_prompt=SUPERVISOR_PROMPT,
        #checkpointer=InMemorySaver()
    )
   


query = (
    "Schedule a meeting for me with the design team next week saturday at 3pm for an hour"
    "and send them an email reminder about reviewing the new mockups"
)

config = {"configurable" : {"thread_id": "6"}}

for step in supervisor_agent.stream(
    {"messages": [{"role": "user", "content": query}]}
):
    for update in step.values():
        for message in update.get("messages", []):
            message.pretty_print()

# def return_interrupts():
#     interrupts = []
#     for step in supervisor_agent.stream(
#         {"messages": [{"role": "user", "content": query}]},
#         #config
#     ):
#         for update in step.values():
#             if isinstance(update, dict):
#                 for message in update.get("messages", []):
#                     message.pretty_print()
#             else:
#                 interrupt_ = update[0]
#                 interrupts.append(interrupt_)
#                 print(f"\nINTERRUPTED: {interrupt_.id}")

#     for interrupt_ in interrupts:
#         for request in interrupt_.value["action_requests"]:
#             print(f"INTERRUPTED: {interrupt_.id}")
#             print(f"{request['description']}\n")
#     return interrupts

# return_interrupts()
            