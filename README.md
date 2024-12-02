# Enterprise State Machine Framework

## Overview
This repository contains an advanced, enterprise-grade state machine framework designed for robust workflow management. The framework supports multiple integration patterns, comprehensive error handling, and detailed audit trails.

## Core Features

### Global Handlers
- **Callback Handler**: Global webhook configuration for centralized callback management
- **Error Handler**: Configurable global error handling strategies
  - Error Actions: abort, rollback, retry, ignore, notify, log
  - Timeout Actions: retry, proceed, notify, escalate

### Integration Patterns
The framework supports three primary integration patterns:

1. **Webhook Integration**
   - RESTful HTTP endpoints
   - Configurable methods and payloads
   - Response validation
   - Condition-based processing

2. **Kafka Integration**
   - Topic-based messaging
   - Message payload configuration
   - Expected message validation
   - Conditional processing

3. **File System Integration**
   - File-based triggers and callbacks
   - Content validation
   - Path-based processing
   - File system monitoring

### State Management

#### State Components
- Unique identifier and metadata
- Base state types (initial, intermediate, final)
- Custom state types for business logic
- Data payload storage
- Entry and exit actions

#### Action Configuration
- Retry mechanisms
  - Configurable retry count
  - Delay between retries (ISO 8601 duration)
- Timeout handling
  - Duration specification
  - Timeout actions
- Status tracking (pending, in-progress, completed, failed)
- Error handling strategies

### Transition System
- Event-driven transitions
- Multiple trigger types
  - Manual
  - Automatic
  - Time-based
- Action execution during transitions
- Conditional routing

### Audit and Monitoring

#### Audit Trail
- Timestamp tracking
- Action logging
- User attribution
- Detailed event information
- Custom metadata support

#### Version Control
- State machine versioning
- Change tracking
- Update history

## Implementation Guide

### Configuration Setup
```json
{
  "stateMachineId": "unique-identifier",
  "version": 1,
  "globalCallbackHandler": {
    "webhook": {
      "url": "https://api.example.com/callback",
      "method": "POST"
    }
  }
}
```

### Error Handling Configuration
```json
{
  "globalErrorHandler": {
    "onError": "retry",
    "onTimeout": "notify"
  }
}
```

### Action Configuration
```json
{
  "actionId": "action-identifier",
  "retryCount": 3,
  "retryDelay": "PT10S",
  "timeout": "PT1M"
}
```

## Money Transfer State Machine

## Overview
A robust state machine implementation for handling secure money transfers between accounts. This system ensures reliable, traceable, and secure money transfer operations through a series of well-defined states and transitions.

## Directory Structure
```
.
├── README.md
├── definitions/
│   └── money-transfer-definition.json    # State machine definition
└── instances/
    └── money-transfer-instance.json      # Example instance
```

## State Machine Definition

### Core Components

#### Global Configuration
- **State Machine ID**: `moneyTransferSM`
- **Version**: 1
- **Global Callback Handler**: Centralized webhook for monitoring
- **Global Error Handler**: Configurable error and timeout strategies

#### Data Schemas
Each state enforces strict JSON schema validation for its data:
- **Transfer ID**: UUID format
- **Amounts**: Positive decimal numbers
- **Accounts**: Alphanumeric, minimum 8 characters
- **Timestamps**: ISO 8601 format
- **Currencies**: USD, EUR, GBP supported


### Instance Data Management

Instance data is stored in the `instances` directory, following this structure:

```
instances/
├── active/                 # Currently running instances
│   └── instance-123.json
├── completed/             # Successfully completed instances
│   └── instance-456.json
└── error/                # Instances that encountered errors
    └── instance-789.json
```

Example instance data structure:
```json
{
  "instanceId": "instance-123",
  "stateMachineId": "money-transfer",
  "currentState": "verify",
  "startTime": "2024-01-10T14:30:00Z",
  "lastUpdated": "2024-01-10T14:35:00Z",
  "data": {
    "transferId": "tr-123e4567-e89b-12d3-a456-426614174000",
    "amount": 1000.00,
    "currency": "USD",
    "sourceAccount": "ACCT12345678",
    "destinationAccount": "ACCT87654321"
  },
  "history": [
    {
      "state": "init",
      "enteredAt": "2024-01-10T14:30:00Z",
      "exitedAt": "2024-01-10T14:31:00Z",
      "data": { ... }
    },
    {
      "state": "verify",
      "enteredAt": "2024-01-10T14:31:00Z",
      "data": { ... }
    }
  ]
}
```

## Data Validation

### JSON Schema Implementation
Each state enforces strict JSON Schema validation (draft-07) for its data:

#### Common Features
- Schema Version: `http://json-schema.org/draft-07/schema#`
- Additional Properties: Disabled by default
- Required Fields: Explicitly defined per state
- Data Types: Strictly enforced
- Format Validation: UUID, date-time, etc.

#### State-Specific Schemas

1. **Initialization State**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "transferId": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for the transfer"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Time when the transfer was initiated"
    },
    "clientReference": {
      "type": "string",
      "description": "Client's reference number"
    }
  },
  "required": ["transferId", "timestamp"],
  "additionalProperties": false
}
```

2. **Verification State**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "transferId": {
      "type": "string",
      "format": "uuid"
    },
    "amount": {
      "type": "number",
      "minimum": 0.01,
      "description": "Transfer amount"
    },
    "currency": {
      "type": "string",
      "enum": ["USD", "EUR", "GBP"],
      "description": "Transfer currency"
    },
    "sourceAccount": {
      "type": "string",
      "pattern": "^[A-Z0-9]{8,}$",
      "description": "Source account number"
    },
    "destinationAccount": {
      "type": "string",
      "pattern": "^[A-Z0-9]{8,}$",
      "description": "Destination account number"
    }
  },
  "required": [
    "transferId",
    "amount",
    "currency",
    "sourceAccount",
    "destinationAccount"
  ],
  "additionalProperties": false
}
```

### Validation Rules

#### 1. Transfer ID
- Format: UUID v4
- Required in all states
- Immutable once set
- Used for tracking and idempotency

#### 2. Amount
- Minimum: 0.01
- Type: Number (decimal)
- Required in verification state
- Currency must be specified

#### 3. Account Numbers
- Pattern: `^[A-Z0-9]{8,}$`
- Minimum length: 8 characters
- Allowed characters: A-Z, 0-9
- Required for both source and destination

#### 4. Currency
- Allowed values: USD, EUR, GBP
- Required with amount
- Case sensitive

#### 5. Timestamps
- Format: ISO 8601
- Timezone: UTC
- Example: "2024-01-10T14:30:00Z"

### Error States Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "transferId": {
      "type": "string",
      "format": "uuid"
    },
    "errorCode": {
      "type": "string"
    },
    "errorMessage": {
      "type": "string"
    },
    "errorTimestamp": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": ["transferId", "errorCode", "errorMessage"],
  "additionalProperties": false
}
```


## Diagram Generation

The framework includes tools to automatically generate state diagrams from your workflow definitions. This helps visualize the flow and transitions of your state machines.

For detailed instructions on generating and customizing state diagrams, please see our [State Diagram Guide](diagrams.md).

Quick start:
```bash
# Install dependencies
pip3 install -r tools/requirements.txt
brew install graphviz  # macOS only

# Generate state diagram
python3 tools/generators/diagram_generator.py definitions/money-transfer-definition.json --output diagrams/money-transfer-state.md --type state

# Generate sequence diagram
python3 tools/generators/diagram_generator.py definitions/money-transfer-definition.json --output diagrams/money-transfer-sequence.md --type sequence
```

## BPMN Integration

### Converting JSON to BPMN

The framework supports bidirectional conversion between JSON state machine definitions and BPMN format. Use the converter tool:

```bash
python tools/converters/bpmn_converter.py definitions/money-transfer-definition.json diagrams/money-transfer.bpmn --direction json2bpmn
```

Example JSON state machine definition:
```json
{
  "id": "money-transfer",
  "states": {
    "init": {
      "type": "initial",
      "transitions": [
        {
          "target": "verify",
          "trigger": "automatic"
        }
      ]
    },
    "verify": {
      "type": "task",
      "transitions": [
        {
          "target": "process",
          "condition": "data.amount > 0"
        }
      ]
    }
  }
}
```

### Converting BPMN to JSON

To convert existing BPMN files to our JSON format:

```bash
python tools/converters/bpmn_converter.py input.bpmn output.json --direction bpmn2json
```

The converter supports:
- Start events (initial states)
- End events (final states)
- Tasks and User Tasks
- Exclusive Gateways (decision points)
- Boundary Events (error handling)
- Sequence Flows with conditions



## State Flow
```
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Init   │ ──> │  Verify  │ ──> │ Process  │ ──> │ Complete │
└────┬────┘     └────┬─────┘     └────┬─────┘     └──────────┘
     │               │                 │
     │               │                 │
     └───────────────┴─────────────────┘
                     │
                     ▼
               ┌──────────┐
               │  Error   │
               └──────────┘
```

### States in Detail

#### 1. Initialization (init)
- **Purpose**: Creates new transfer request
- **Key Features**:
  - Generates unique transfer ID
  - Records initiation timestamp
  - Captures client reference
- **Validation**:
  - Required: transferId, timestamp
  - Optional: clientReference
- **Retry Configuration**:
  - Count: 3 attempts
  - Delay: 10 seconds
  - Timeout: 1 minute

#### 2. Verification (verify)
- **Purpose**: Comprehensive transfer validation
- **Validations**:
  - Account number format
  - Currency support
  - Minimum amount (0.01)
  - Account existence
  - Balance sufficiency
- **Security Checks**:
  - Account ownership
  - Transfer limits
  - Compliance rules
- **Retry Configuration**:
  - Count: 3 attempts
  - Delay: 5 seconds
  - Timeout: 30 seconds

#### 3. Processing (process)
- **Purpose**: Execute transfer
- **Operations**:
  - Lock source funds
  - Execute transfer
  - Update balances
  - Generate transaction reference
- **Security**:
  - Atomic operations
  - Transaction logging
  - No retry on failure
- **Timeout**: 1 minute

#### 4. Completion (complete)
- **Purpose**: Finalize transfer
- **Operations**:
  - Record final status
  - Send notifications
  - Generate receipts
- **Status Types**:
  - success: Complete transfer
  - partial: Partial completion

#### 5. Error (error)
- **Purpose**: Handle failures
- **Data Captured**:
  - Error code
  - Detailed message
  - Timestamp
  - State of failure
- **Actions**:
  - Notification
  - Logging
  - Recovery steps

### Transitions

#### 1. Init to Verify (initToVerify)
- **Trigger**: Manual start
- **Prerequisites**: 
  - Valid transfer ID
  - Complete initial data

#### 2. Verify to Process (verifyToProcess)
- **Trigger**: Manual verification complete
- **Conditions**:
  - Amount > 0
  - All validations passed
  - Sufficient funds

#### 3. Process to Complete (processToComplete)
- **Trigger**: Manual process complete
- **Prerequisites**:
  - Successful fund transfer
  - Transaction recorded

#### 4. Any to Error (anyToError)
- **Source States**: Init, Verify, Process
- **Triggers**:
  - Validation failure
  - Insufficient funds
  - Technical error
  - Timeout

## Instance Management

### Instance Data Structure
```json
{
  "instanceId": "UUID",
  "stateMachineId": "money-transfer",
  "currentState": "state-id",
  "currentStateData": {},
  "history": [],
  "variables": {},
  "status": "active|completed|error"
}
```