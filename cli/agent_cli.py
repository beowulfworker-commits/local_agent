"""
Command‑line interface for interacting with the local agent.

This script allows you to send messages to the agent from your terminal. By
default, it operates in pure chat mode. Use ``--use-tools`` to allow the
agent to call its registered tools. See docs/LOCAL_AGENT.md for examples.
"""

import argparse
import logging
import sys

from agent import Agent, OllamaBackend


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI for the local Qwen agent")
    parser.add_argument(
        "--use-tools", action="store_true", help="Allow the agent to invoke tools"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="qwen2.5-coder:14b",
        help="Name of the model to use",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    backend = OllamaBackend(model=args.model)
    agent = Agent(backend=backend, tools_config="agent/config/tools.yaml")

    print("Local Qwen Agent CLI. Press Ctrl+C or Ctrl+D to exit.")
    if args.use_tools:
        print("Tool invocation is enabled.")
    else:
        print("Tool invocation is disabled. Use --use-tools to enable.")
    try:
        while True:
            try:
                user_input = input("You: ")
            except EOFError:
                break
            if not user_input.strip():
                continue
            reply = agent.chat(user_input, use_tools=args.use_tools)
            print(f"Agent: {reply}")
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()