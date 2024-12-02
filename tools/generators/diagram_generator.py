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

    def get_transition_label(self, transition):
        if 'name' in transition:
            return transition['name']
        elif 'event' in transition and transition['event'] and len(transition['event']) > 0:
            return transition['event'][0]['name']
        else:
            return transition['transitionId']

    def generate_state_diagram(self) -> str:
        """Generate a Mermaid state diagram."""
        mermaid = ["stateDiagram-v2"]
        
        # Add states
        for state in self.data["states"]:
            state_id = state["stateId"]
            state_name = state.get('name', state_id)
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
            label = self.get_transition_label(transition)
            
            # Handle array of from states
            if isinstance(from_state, list):
                for state in from_state:
                    mermaid.append(f"    {state} --> {to_state}: {label}")
            else:
                mermaid.append(f"    {from_state} --> {to_state}: {label}")

        return "\n".join(mermaid)

    def generate_sequence_diagram(self) -> str:
        """Generate a Mermaid sequence diagram."""
        mermaid = ["sequenceDiagram"]
        mermaid.append("    participant User")
        mermaid.append("    participant System")
        
        current_state = None
        
        for transition in self.transitions:
            from_state = transition['fromStateId']
            to_state = transition['toStateId']
            label = self.get_transition_label(transition)
            
            if current_state != from_state:
                mermaid.append(f"    Note over User,System: State: {from_state}")
                current_state = from_state
            
            # Handle user-triggered transitions
            if 'trigger' in transition.get('event', [{}])[0] and transition['event'][0]['trigger'] == 'manual':
                mermaid.append(f"    User->>+System: {label}")
                if 'entryActions' in next((s for s in self.data["states"] if s['stateId'] == to_state), {}):
                    mermaid.append(f"    System->>System: Execute {to_state} actions")
                mermaid.append(f"    System-->>-User: State updated to {to_state}")
            # Handle system-triggered transitions
            else:
                mermaid.append(f"    activate System")
                mermaid.append(f"    System->>System: {label}")
                if 'entryActions' in next((s for s in self.data["states"] if s['stateId'] == to_state), {}):
                    mermaid.append(f"    System->>System: Execute {to_state} actions")
                mermaid.append(f"    System-->>User: State updated to {to_state}")
                mermaid.append(f"    deactivate System")

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
