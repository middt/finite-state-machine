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

## Best Practices

### Error Handling
1. Configure appropriate retry counts based on action criticality
2. Set meaningful timeout durations
3. Implement escalation paths for critical failures
4. Use appropriate error handling strategies per action type

### Integration
1. Use webhook timeouts appropriate for the endpoint
2. Implement idempotency in callbacks
3. Configure meaningful expected responses
4. Use appropriate security measures for endpoints

### Monitoring
1. Implement comprehensive logging
2. Set up alerts for critical state transitions
3. Monitor audit trails for anomalies
4. Track performance metrics

### Security
1. Implement authentication for webhooks
2. Secure sensitive data in state payloads
3. Implement access control for state transitions
4. Audit all security-relevant events

## Performance Considerations
- Configure appropriate timeout values
- Implement efficient retry strategies
- Use appropriate integration patterns for scale
- Monitor resource usage in actions

## Scalability
- Horizontally scalable design
- Stateless operation support
- Distributed execution capability
- Event-driven architecture

## Future Enhancements
1. Dynamic state definition
2. Custom integration patterns
3. Advanced monitoring capabilities
4. Machine learning-based optimization
5. Enhanced security features

## Contributing
Please refer to CONTRIBUTING.md for guidelines on how to contribute to this project.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

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

### Validation Best Practices

1. **Input Validation**
   - Validate before state transitions
   - Check data types and formats
   - Verify required fields
   - Validate business rules

2. **Error Handling**
   - Provide clear error messages
   - Include validation details
   - Log validation failures
   - Support error recovery

3. **Schema Evolution**
   - Version schemas explicitly
   - Maintain backward compatibility
   - Document schema changes
   - Support schema migration

4. **Performance Considerations**
   - Cache compiled schemas
   - Optimize regex patterns
   - Monitor validation times
   - Handle large payloads efficiently

## Diagram Generation

The framework includes tools to automatically generate state diagrams from your workflow definitions. This helps visualize the flow and transitions of your state machines.

For detailed instructions on generating and customizing state diagrams, please see our [State Diagram Guide](diagrams.md).

Quick start:
```bash
# Install dependencies
pip3 install -r tools/requirements.txt
brew install graphviz  # macOS only

# Generate state diagram
python3 tools/diagram_generator.py definitions/money-transfer-definition.json --output diagrams/money-transfer-state.md --type state

# Generate sequence diagram
python3 tools/diagram_generator.py definitions/money-transfer-definition.json --output diagrams/money-transfer-sequence.md --type sequence
```

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
  "currentState": "state-id",
  "currentStateData": {},
  "history": [],
  "variables": {},
  "status": "active|completed|error"
}
```

### State History
- Complete audit trail
- Entry/exit timestamps
- Action execution details
- Data snapshots

### Variables
- Retry counters
- Error tracking
- User information
- Priority levels

## Integration

### Webhook Configuration
Each integration point requires:
- Endpoint URL
- HTTP method
- Expected response
- Timeout settings
- Retry policy

### Webhook Endpoints
1. **Initialize**: `/initialize`
   - Purpose: Start transfer
   - Method: POST
   - Payload: transferId, status

2. **Verify**: `/verify`
   - Purpose: Validate details
   - Method: POST
   - Payload: transferId, amount, accounts

3. **Process**: `/process`
   - Purpose: Execute transfer
   - Method: POST
   - Payload: transferId, transaction details

4. **Complete**: `/complete`
   - Purpose: Finalize transfer
   - Method: POST
   - Payload: transferId, status

5. **Error**: `/error`
   - Purpose: Handle failures
   - Method: POST
   - Payload: transferId, errorDetails

## Error Handling

### Retry Mechanisms
- Configurable retry counts
- Exponential backoff
- State-specific policies

### Error Types
1. **Validation Errors**
   - Invalid data format
   - Business rule violations
   - Insufficient funds

2. **Technical Errors**
   - System unavailable
   - Network timeout
   - Integration failure

3. **Business Errors**
   - Limit exceeded
   - Account frozen
   - Compliance violation

## Monitoring

### Key Metrics
1. **Performance**
   - State transition times
   - Action execution duration
   - End-to-end completion time

2. **Reliability**
   - Error rates
   - Retry counts
   - Success/failure ratio

3. **Business Metrics**
   - Transfer volumes
   - Amount distributions
   - Error patterns

### Audit Trail
- Complete state history
- Action execution logs
- Data changes
- Error details

## Security Considerations

### Data Protection
- Sensitive data encryption
- Secure communication
- Access control

### Compliance
- Transaction logging
- Audit trail
- Error tracking

### Validation
- Input sanitization
- Business rule enforcement
- Amount limits

## Best Practices

### Implementation
1. **Idempotency**
   - Unique transfer IDs
   - Idempotency keys
   - State transition checks

2. **Resilience**
   - Retry mechanisms
   - Circuit breakers
   - Timeout handling

3. **Monitoring**
   - Performance metrics
   - Error tracking
   - Business analytics

### Operations
1. **Deployment**
   - Version control
   - Configuration management
   - Environment separation

2. **Maintenance**
   - Regular audits
   - Performance optimization
   - Security updates

## API Examples

### Initialize Transfer
```json
POST /initialize
{
  "transferId": "tr-123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2024-01-10T14:30:00Z",
  "clientReference": "CLIENT-REF-001"
}
```

### Verify Transfer
```json
POST /verify
{
  "transferId": "tr-123e4567-e89b-12d3-a456-426614174000",
  "amount": 1000.00,
  "currency": "USD",
  "sourceAccount": "ACCT12345678",
  "destinationAccount": "ACCT87654321"
}
```

## Development Guide

### Setup
1. Clone repository
2. Configure webhook endpoints
3. Set up monitoring
4. Configure error handling

### Testing
1. Unit tests for state transitions
2. Integration tests for webhooks
3. Performance testing
4. Error scenario testing

## Contributing
Please see CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
