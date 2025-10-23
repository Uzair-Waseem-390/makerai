from agents import Runner, set_tracing_disabled
from my_agents.visionary_agent import visionary_agent

set_tracing_disabled(True)


while True:
    prompt = input("Write your prompt(or exit): ")
    if prompt.lower() == "exit":
        break
    res = Runner.run_sync(
        starting_agent=visionary_agent,
        input=prompt
    )
    print(f"Agent Name: {res.last_agent.name}")
    print("Final Result:", res.final_output)



