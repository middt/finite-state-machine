#!/usr/bin/env python3

import json
import argparse
import xmltodict
from typing import Dict, List, Union, Any
import os

class BPMNConverter:
    def __init__(self):
        self.state_type_mapping = {
            "initial": "startEvent",
            "final": "endEvent",
            "intermediate": "task",
            "error": "boundaryEvent",
            "user": "userTask",
            "decision": "exclusiveGateway"
        }
        
        self.reverse_type_mapping = {v: k for k, v in self.state_type_mapping.items()}
        self.x_spacing = 150
        self.y_spacing = 100

    def get_transition_event_name(self, transition: Dict[str, Any]) -> str:
        """Extract event name from transition."""
        if "event" in transition and isinstance(transition["event"], list) and transition["event"]:
            return transition["event"][0].get("name", "")
        return ""

    def get_state_by_id(self, states: List[Dict], state_id: str) -> Dict:
        """Get state by its ID."""
        for state in states:
            if state["stateId"] == state_id:
                return state
        return None

    def is_decision_point(self, state_id: str, transitions: List[Dict]) -> bool:
        """Check if a state is a decision point (has multiple outgoing transitions)."""
        outgoing_transitions = [t for t in transitions if t["fromStateId"] == state_id]
        return len(outgoing_transitions) > 1

    def is_user_task(self, state: Dict) -> bool:
        """Check if a state represents a user task."""
        events = []
        for transition in state.get("transitions", []):
            events.extend(transition.get("event", []))
        
        return any(event.get("trigger") == "manual" for event in events)

    def find_attached_task(self, error_state_id: str, transitions: List[Dict], states: List[Dict]) -> str:
        """Find the task that an error boundary event should be attached to."""
        # Find the transition that leads to this error state
        for transition in transitions:
            if transition["toStateId"] == error_state_id:
                from_state = self.get_state_by_id(states, transition["fromStateId"])
                if from_state:
                    return from_state["stateId"]
        return None

    def create_bpmn_di(self, process_id: str, elements: Dict) -> Dict:
        """Create BPMN diagram information."""
        diagram = {
            "bpmndi:BPMNDiagram": {
                "@id": f"BPMNDiagram_{process_id}",
                "bpmndi:BPMNPlane": {
                    "@id": f"BPMNPlane_{process_id}",
                    "@bpmnElement": process_id,
                    "bpmndi:BPMNShape": [],
                    "bpmndi:BPMNEdge": []
                }
            }
        }

        # Create state position mapping
        state_positions = {}
        x, y = 100, 100
        
        # First pass: create shapes for all non-boundary events
        for state in elements["states"]:
            if state["baseStateType"] != "error":
                state_id = state["stateId"]
                
                # Determine if this is a decision point
                if self.is_decision_point(state_id, elements["transitions"]):
                    state["baseStateType"] = "decision"
                
                # Determine if this is a user task
                if self.is_user_task(state):
                    state["baseStateType"] = "user"

                # Calculate shape dimensions
                if state["baseStateType"] in ["initial", "final"]:
                    width = 36
                    height = 36
                elif state["baseStateType"] == "decision":
                    width = 50
                    height = 50
                else:
                    width = 120
                    height = 80
                
                shape = {
                    "@id": f"Shape_{state_id}",
                    "@bpmnElement": state_id,
                    "dc:Bounds": {
                        "@x": str(x),
                        "@y": str(y),
                        "@width": str(width),
                        "@height": str(height)
                    }
                }
                diagram["bpmndi:BPMNDiagram"]["bpmndi:BPMNPlane"]["bpmndi:BPMNShape"].append(shape)
                
                # Store position for edge creation
                state_positions[str(state_id)] = {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height
                }
                
                x += self.x_spacing
                if x > 600:  # Start new row
                    x = 100
                    y += self.y_spacing

        # Second pass: add boundary events
        for state in elements["states"]:
            if state["baseStateType"] == "error":
                state_id = state["stateId"]
                width = 36
                height = 36
                
                attached_task_id = self.find_attached_task(state_id, elements["transitions"], elements["states"])
                if attached_task_id and attached_task_id in state_positions:
                    task_pos = state_positions[attached_task_id]
                    x = task_pos["x"] + task_pos["width"] - width/2
                    y = task_pos["y"] + task_pos["height"] - height/2
                    
                    shape = {
                        "@id": f"Shape_{state_id}",
                        "@bpmnElement": state_id,
                        "dc:Bounds": {
                            "@x": str(x),
                            "@y": str(y),
                            "@width": str(width),
                            "@height": str(height)
                        }
                    }
                    diagram["bpmndi:BPMNDiagram"]["bpmndi:BPMNPlane"]["bpmndi:BPMNShape"].append(shape)
                    
                    state_positions[str(state_id)] = {
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height
                    }

        # Third pass: create edges
        for transition in elements["transitions"]:
            from_state_id = str(transition["fromStateId"])
            to_state_id = str(transition["toStateId"])
            
            from_state = state_positions.get(from_state_id)
            to_state = state_positions.get(to_state_id)
            
            if from_state and to_state:
                # Calculate connection points
                source_x = from_state["x"] + from_state["width"]
                source_y = from_state["y"] + (from_state["height"] / 2)
                target_x = to_state["x"]
                target_y = to_state["y"] + (to_state["height"] / 2)
                
                # For boundary events, adjust the connection points
                if self.get_state_by_id(elements["states"], to_state_id)["baseStateType"] == "error":
                    target_x = to_state["x"] + to_state["width"]/2
                    target_y = to_state["y"]
                
                edge = {
                    "@id": f"Edge_{transition['transitionId']}",
                    "@bpmnElement": transition["transitionId"],
                    "di:waypoint": [
                        {"@x": str(source_x), "@y": str(source_y)},
                        {"@x": str(target_x), "@y": str(target_y)}
                    ]
                }
                diagram["bpmndi:BPMNDiagram"]["bpmndi:BPMNPlane"]["bpmndi:BPMNEdge"].append(edge)

        return diagram

    def json_to_bpmn(self, json_data: Dict) -> Dict:
        """Convert state machine JSON definition to BPMN XML structure."""
        process_id = json_data["stateMachineId"]
        
        # Create basic BPMN structure
        bpmn = {
            "definitions": {
                "@xmlns": "http://www.omg.org/spec/BPMN/20100524/MODEL",
                "@xmlns:bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
                "@xmlns:dc": "http://www.omg.org/spec/DD/20100524/DC",
                "@xmlns:di": "http://www.omg.org/spec/DD/20100524/DI",
                "@xmlns:modeler": "http://camunda.org/schema/modeler/1.0",
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "@targetNamespace": "http://bpmn.io/schema/bpmn",
                "@id": f"Definitions_{process_id}",
                "process": {
                    "@id": process_id,
                    "@isExecutable": "true"
                }
            }
        }

        # First pass: identify decision points and user tasks
        for state in json_data["states"]:
            if self.is_decision_point(state["stateId"], json_data["transitions"]):
                state["baseStateType"] = "decision"
            if self.is_user_task(state):
                state["baseStateType"] = "user"

        # Group states by type
        state_groups = {}
        for state in json_data["states"]:
            bpmn_type = self.state_type_mapping.get(state["baseStateType"], "task")
            if bpmn_type not in state_groups:
                state_groups[bpmn_type] = []
            
            element = {
                "@id": state["stateId"],
                "@name": state["name"]
            }
            
            # Add gateway-specific attributes
            if bpmn_type == "exclusiveGateway":
                element["@gatewayDirection"] = "Diverging"
            
            # Add boundary event attributes
            if bpmn_type == "boundaryEvent":
                attached_task_id = self.find_attached_task(state["stateId"], json_data["transitions"], json_data["states"])
                if attached_task_id:
                    element["@attachedToRef"] = attached_task_id
                    element["@cancelActivity"] = "true"
            
            # Add documentation if available
            if state.get("description"):
                element["documentation"] = {"text": state["description"]}
            
            state_groups[bpmn_type].append(element)

        # Add states to process in correct order
        state_type_order = ["startEvent", "task", "userTask", "exclusiveGateway", "boundaryEvent", "endEvent"]
        for bpmn_type in state_type_order:
            if bpmn_type in state_groups and state_groups[bpmn_type]:
                bpmn["definitions"]["process"][bpmn_type] = state_groups[bpmn_type]

        # Add transitions
        sequence_flows = []
        for transition in json_data["transitions"]:
            event_name = self.get_transition_event_name(transition)
            
            flow = {
                "@id": transition["transitionId"],
                "@sourceRef": transition["fromStateId"],
                "@targetRef": transition["toStateId"],
                "@name": event_name
            }
            
            # Add condition if present
            if "condition" in transition and transition["condition"] != "true":
                flow["conditionExpression"] = {
                    "@xsi:type": "tFormalExpression",
                    "#text": transition["condition"]
                }
            
            # Handle special case for error transitions
            if isinstance(transition.get("fromStateId"), list):
                # Create a boundary event for each source state
                for source_id in transition["fromStateId"]:
                    error_flow = flow.copy()
                    error_flow["@id"] = f"{flow['@id']}_{source_id}"
                    error_flow["@sourceRef"] = source_id
                    sequence_flows.append(error_flow)
            elif transition.get("fromStateId") == "any":
                # Create a boundary event for each possible source state
                possible_sources = [s["stateId"] for s in json_data["states"] 
                                 if s["baseStateType"] not in ["initial", "final", "error"]]
                for source_id in possible_sources:
                    error_flow = flow.copy()
                    error_flow["@id"] = f"{flow['@id']}_{source_id}"
                    error_flow["@sourceRef"] = source_id
                    sequence_flows.append(error_flow)
            else:
                sequence_flows.append(flow)
        
        if sequence_flows:
            bpmn["definitions"]["process"]["sequenceFlow"] = sequence_flows

        # Add diagram information
        bpmn["definitions"].update(self.create_bpmn_di(process_id, json_data))

        return bpmn

    def bpmn_to_json(self, bpmn_data: Dict) -> Dict:
        """Convert BPMN XML structure to state machine JSON definition."""
        process = bpmn_data["definitions"]["process"]
        
        # Create basic state machine structure
        state_machine = {
            "stateMachineId": process["@id"],
            "name": process.get("@name", "Converted from BPMN"),
            "description": "Converted from BPMN format",
            "version": 1,
            "states": [],
            "transitions": []
        }

        # Helper function to process BPMN elements
        def process_elements(elements, bpmn_type):
            if not isinstance(elements, list):
                elements = [elements]
                
            for element in elements:
                state_type = self.reverse_type_mapping.get(bpmn_type, "intermediate")
                
                state = {
                    "stateId": element["@id"],
                    "name": element.get("@name", element["@id"]),
                    "description": element.get("documentation", {}).get("text", ""),
                    "baseStateType": state_type,
                    "stateType": "process",
                    "data": {
                        "schema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
                
                # Add gateway-specific properties
                if bpmn_type == "exclusiveGateway":
                    state["stateType"] = "decision"
                elif bpmn_type == "userTask":
                    state["stateType"] = "user"
                elif bpmn_type == "boundaryEvent":
                    state["attachedTo"] = element.get("@attachedToRef")
                
                state_machine["states"].append(state)

        # Convert BPMN elements to states
        for bpmn_type in self.state_type_mapping.values():
            if bpmn_type in process:
                process_elements(process[bpmn_type], bpmn_type)

        # Convert sequence flows to transitions
        flows = process.get("sequenceFlow", [])
        if not isinstance(flows, list):
            flows = [flows]
            
        for flow in flows:
            transition = {
                "transitionId": flow["@id"],
                "fromStateId": flow["@sourceRef"],
                "toStateId": flow["@targetRef"],
                "event": [{
                    "eventId": f"evt_{flow['@id']}",
                    "name": flow.get("@name", ""),
                    "description": "",
                    "trigger": "manual" if any(s["stateType"] == "user" for s in state_machine["states"] if s["stateId"] == flow["@sourceRef"]) else "auto"
                }] if flow.get("@name") else [],
                "condition": flow.get("conditionExpression", {}).get("#text", "true")
            }
            state_machine["transitions"].append(transition)

        return state_machine

def save_xml(bpmn_data: Dict, output_file: str):
    """Save BPMN dictionary as XML file."""
    xml_str = xmltodict.unparse(bpmn_data, pretty=True)
    # Remove any existing XML declaration
    if xml_str.startswith('<?xml'):
        xml_str = xml_str[xml_str.find('?>')+2:].lstrip()
    # Add our own XML declaration
    final_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_xml)

def save_json(json_data: Dict, output_file: str):
    """Save JSON dictionary to file."""
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Convert between State Machine JSON and BPMN XML formats')
    parser.add_argument('input_file', help='Input file path (JSON or BPMN XML)')
    parser.add_argument('output_file', help='Output file path')
    parser.add_argument('--direction', choices=['json2bpmn', 'bpmn2json'], required=True,
                      help='Conversion direction')
    
    args = parser.parse_args()
    
    converter = BPMNConverter()
    
    # Read input file
    with open(args.input_file, 'r') as f:
        if args.direction == 'json2bpmn':
            input_data = json.load(f)
            output_data = converter.json_to_bpmn(input_data)
            save_xml(output_data, args.output_file)
        else:  # bpmn2json
            input_data = xmltodict.parse(f.read())
            output_data = converter.bpmn_to_json(input_data)
            save_json(output_data, args.output_file)
    
    print(f"Conversion completed. Output saved to: {args.output_file}")

if __name__ == "__main__":
    main()
