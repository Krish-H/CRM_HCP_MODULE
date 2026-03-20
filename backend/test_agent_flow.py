from agent import run_agent

print("--- REGULAR CHAT INPUT ---")
print(run_agent("fix this, met Dr.Black , discussed efficacy,gave 2 samples,sentiment positive,follow up today"))

print("\n--- FORM SUBMISSION INPUT ---")
print(run_agent('''
        Log interaction:
        Doctor: Dr. Smith
        Topics: Efficacy
        Samples: 5 boxes
        Sentiment: Positive
        Next Steps: Follow up tomorrow
        Notes: Good chat.
'''))
