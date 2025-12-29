from agent import return_interrupts, supervisor_agent
from langgraph.types import Command

supervisor = supervisor_agent()
config = {"configurable" : {"thread_id": "6"}}
interrupts = return_interrupts()
resume = {}
for interrupt_ in interrupts:
    if interrupt_.id == "cd8f6bbe02909058033504950a728037" :
        edited_action = interrupt_.value["action_requests"][0].copy()
        edited_action["arguments"]["subject"] = "Mockups reminder"
        resume[interrupt_.id] = {
            "decisions" : [{"type" : "edit", "edited_action" : edited_action}]
        }
    else:
        resume[interrupt_.id] = {"decisions" : [{"type" : "approve"}]}

interrupts = []
for steps in supervisor.stream(
    Command(resume=resume),
    config,
):
    for update in steps.values():
        if isinstance(update, dict):
            for message in update.get("messages", []):
                message.pretty_print()
        else:
            interrupt_ = update[0]
            interrupts.append(interrupt_)
            print(f"\nINTERRUPTED: {interrupt_.id}")