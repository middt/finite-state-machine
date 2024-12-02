#!/usr/bin/env python3
import json
import sys
from typing import Dict, List
import argparse

class DiagramGenerator:
    def __init__(self, json_data: Dict):
        self.data = json_data
        self.states = {state["stateId"]: state for state in json_data["states"]}
        self.transitions = json_data["transitions"]

    def generate_state_diagram(self) -> str:
        """Generate a Mermaid state diagram."""
        mermaid = ["stateDiagram-v2"]
        
        # Add states
        for state in self.data["states"]:
            state_id = state["stateId"]
            state_name = state["name"]
            state_type = state["baseStateType"]
            
            # Add state with description
            if state_type == "initial":
                mermaid.append(f"    [*] --> {state_id}")
            elif state_type == "final":
                mermaid.append(f"    {state_id} --> [*]")
            
            # Add state description
            mermaid.append(f"    {state_id}: {state_name}")
            
        # Add transitions
        for transition in self.transitions:
            from_state = transition["fromStateId"]
            to_state = transition["toStateId"]
            
            # Handle array of from states
            if isinstance(from_state, list):
                for state in from_state:
                    mermaid.append(f"    {state} --> {to_state}: {transition['event'][0]['name']}")
            else:
                mermaid.append(f"    {from_state} --> {to_state}: {transition['event'][0]['name']}")

        return "\n".join(mermaid)

    def generate_sequence_diagram(self) -> str:
        """Generate a Mermaid sequence diagram."""
        mermaid = ["sequenceDiagram"]
        mermaid.append("    participant C as Client")
        mermaid.append("    participant SM as State Machine")
        
        # Add all unique webhook endpoints as participants
        webhooks = set()
        for state in self.data["states"]:
            for action in state.get("entryActions", []):
                if "webhook" in action.get("trigger", {}):
                    webhook_url = action["trigger"]["webhook"]["url"]
                    webhooks.add(webhook_url)
        
        for webhook in sorted(webhooks):
            service_name = webhook.split("/")[-1].capitalize()
            mermaid.append(f"    participant {service_name} as {service_name} Service")
        
        # Add state transitions and webhook calls
        for transition in self.transitions:
            from_state = transition["fromStateId"]
            to_state = transition["toStateId"]
            event_name = transition["event"][0]["name"]
            
            # Add transition event
            mermaid.append(f"    C->>+SM: {event_name}")
            mermaid.append(f"    SM->>SM: Transition from {from_state} to {to_state}")
            
            # Add webhook calls for the target state
            if isinstance(to_state, str):  # Handle single state
                target_state = self.states[to_state]
                for action in target_state.get("entryActions", []):
                    if "webhook" in action.get("trigger", {}):
                        webhook = action["trigger"]["webhook"]
                        service_name = webhook["url"].split("/")[-1].capitalize()
                        mermaid.append(f"    SM->>+{service_name}: {webhook['method']} {webhook['url']}")
                        mermaid.append(f"    {service_name}-->>-SM: Response")
            
            mermaid.append(f"    SM-->>-C: State updated to {to_state}")
            mermaid.append("")  # Add spacing between transitions

        return "\n".join(mermaid)

def main():
    parser = argparse.ArgumentParser(description='Generate Mermaid diagrams from state machine definition')
    parser.add_argument('input_file', help='Input JSON file path')
    parser.add_argument('--type', choices=['state', 'sequence', 'all'], default='all',
                      help='Type of diagram to generate (default: all)')
    parser.add_argument('--output', help='Output markdown file path')
    
    args = parser.parse_args()
    
    # Read JSON file
    with open(args.input_file, 'r') as f:
        json_data = json.load(f)
    
    # Create generator
    generator = DiagramGenerator(json_data)
    
    # Generate diagrams
    output = []
    if args.type in ['state', 'all']:
        output.extend([
            "# State Diagram",
            "```mermaid",
            generator.generate_state_diagram(),
            "```\n"
        ])
    
    if args.type in ['sequence', 'all']:
        output.extend([
            "# Sequence Diagram",
            "```mermaid",
            generator.generate_sequence_diagram(),
            "```\n"
        ])
    
    # Output results
    output_content = "\n".join(output)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_content)
        print(f"Diagrams written to {args.output}")
    else:
        print(output_content)

if __name__ == "__main__":
    main()
