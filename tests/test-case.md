### C.1 Model Type Testing

| ID | Test Case | Test Description | Precondition | Test Steps | Input | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|---|---|
| TC-M01 | test_model_structure_detection | Verify system can detect differences in model structures | System started, server running normally | 1. Prepare standard model structure<br>2. Prepare different model structure<br>3. Run model structure detection | Standard model: {'layer_names': ['conv1', 'conv2', 'fc1', 'fc2', 'fc3'], 'layer_shapes': ['Conv2d(1,6)', 'Conv2d(6,16)', 'Linear(256,120)', 'Linear(120,84)', 'Linear(84,10)']}<br>Different model: {'layer_names': ['conv1', 'conv2', 'fc1', 'fc2'], 'layer_shapes': ['Conv2d(1,8)', 'Conv2d(8,16)', 'Linear(400,100)', 'Linear(100,10)']} | System can detect model structure differences | Model structure detection working correctly | Pass |
| TC-M02 | test_server_parameter_comparison | Verify server can detect parameter count differences | System started, server running normally | 1. Prepare standard model<br>2. Prepare different model<br>3. Server compares parameter counts | Standard model parameter count: 10<br>Different model parameter count: 8 | Server detects parameter count difference | Server can detect parameter count differences | Pass |
| TC-M03 | test_warning_trigger_condition | Verify warning triggers when parameters mismatch | System started, server running normally | 1. Simulate parameter shape mismatch scenario<br>2. Check if warning is triggered | Parameter shape mismatch (expected: [(10, 10), (20, 20)], received: [(15, 15), (25, 25)]) | Trigger warning showing mismatch reason | Warning triggered: {'client_id': 2, 'reason': 'Parameter shape mismatch', 'expected': [(10, 10), (20, 20)], 'received': [(15, 15), (25, 25)]} | Pass |
| TC-M04 | test_client_parameter_shape_logging | Verify server records parameter shapes for each client | System started, multiple clients connected | 1. Clients submit parameters<br>2. Server records parameter shapes<br>3. Check if recording is correct | Client parameters (cid1: [(3,), (2, 2)], cid2: [(3,), (2, 2)]) | Server records parameter shapes for each client | Recorded parameter shapes: [{'cid': 1, 'shapes': [(3,), (2, 2)]}, {'cid': 2, 'shapes': [(3,), (2, 2)]}] | Pass |

---

### C.2 Flower Communication Protocol Testing

| ID | Test Case | Test Description | Precondition | Test Steps | Input | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|---|---|
| TC-F01 | test_client_handshake_sequence | Verify client handshake sequence correctness | Flower server running, client ready to connect | 1. Start client connecting to server<br>2. Record communication sequence | Client connection request | Handshake sequence correct | Expected sequence: connect → acknowledge → get_parameters → parameters<br>Actual sequence: ['connect', 'acknowledge', 'get_parameters', 'parameters'] | Pass |
| TC-F02 | test_heartbeat_protocol | Verify heartbeat communication works normally | Client connected, server running | 1. Start heartbeat monitoring<br>2. Record heartbeat intervals | Heartbeat interval setting | Heartbeat protocol works normally | Heartbeat 0: 1774790911.729<br>Heartbeat 1: 1774790911.834<br>Heartbeat 2: 1774790911.935 | Pass |
| TC-F03 | test_parallel_client_execution | Verify multiple clients execute in parallel | Server running, multiple clients ready | 1. Start multiple clients simultaneously<br>2. Record start and end time for each client | Multiple parallel client requests | All clients execute simultaneously without blocking | Client 1: start=1774790912.040, end=1774790912.145<br>Client 4: start=1774790912.041, end=1774790912.145<br>Client 2: start=1774790912.040, end=1774790912.145<br>Client 3: start=1774790912.040, end=1774790912.145 | Pass |
| TC-F04 | test_round_completion_sequence | Verify complete training round sequence | Server running, multiple clients connected | 1. Execute one complete training round<br>2. Record all communication steps | One round training process | Aggregation operation executes after all client updates | Sequence steps:<br>  - ('server', 'waiting_for_clients', 1)<br>  - ('client', 'receive_parameters', 1, 1)<br>  - ('client', 'local_training', 1, 1)<br>  - ('client', 'send_update', 1, 1)<br>  - ('client', 'receive_parameters', 1, 2)<br>  - ('client', 'local_training', 1, 2)<br>  - ('client', 'send_update', 1, 2)<br>  - ('server', 'aggregate', 1)<br>  - ('server', 'evaluate', 1)<br>  - ('server', 'broadcast', 1) | Pass |
| TC-F05 | test_client_timeout_detection | Verify timeout client detection | Server running, some clients intentionally unresponsive | 1. Start multiple clients<br>2. Make one client unresponsive<br>3. Check timeout detection | Timeout threshold setting | Server detects timeout clients | Round 1: 1 client(s) timed out<br>Number of missing clients: 1 | Pass |
| TC-F06 | test_reconnection_handling | Verify disconnected client reconnection | Server running, client previously disconnected | 1. Simulate client disconnection<br>2. Let client reconnect<br>3. Check reconnection handling | Client reconnection request | System correctly handles reconnection | Reconnection record: [{'cid': 1, 'missed_rounds': 2, 'reconnected': True}] | Pass |

---

### C.3 Model Aggregation Testing

| ID | Test Case | Test Description | Precondition | Test Steps | Input | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|---|---|
| TC-A01 | test_fedavg_aggregation | Verify standard FedAvg aggregation | Server running, 3 clients submitting models | 1. Client 1 submits all-ones matrix<br>2. Client 2 submits all-twos matrix<br>3. Client 3 submits all-threes matrix<br>4. Execute FedAvg aggregation | Client 1: 5×5 all-ones matrix<br>Client 2: 5×5 all-twos matrix<br>Client 3: 5×5 all-threes matrix | Aggregation result = all-twos matrix | Model 1: [[1. 1. 1. 1. 1.],[1. 1. 1. 1. 1.],[1. 1. 1. 1. 1.],[1. 1. 1. 1. 1.],[1. 1. 1. 1. 1.]]<br>Model 2: [[2. 2. 2. 2. 2.],[2. 2. 2. 2. 2.],[2. 2. 2. 2. 2.],[2. 2. 2. 2. 2.],[2. 2. 2. 2. 2.]]<br>Model 3: [[3. 3. 3. 3. 3.],[3. 3. 3. 3. 3.],[3. 3. 3. 3. 3.],[3. 3. 3. 3. 3.],[3. 3. 3. 3. 3.]]<br>Aggregated result: [[2. 2. 2. 2. 2.],[2. 2. 2. 2. 2.],[2. 2. 2. 2. 2.],[2. 2. 2. 2. 2.],[2. 2. 2. 2. 2.]] | Pass |
| TC-A02 | test_single_client_aggregation | Verify single client aggregation | Server running, only 1 client submitting model | 1. Client submits parameters<br>2. Execute aggregation | Client parameters ([[1. 2.],[3. 4.]]) | Aggregation result = client parameters | Original parameters: [[1. 2.],[3. 4.]]<br>Aggregated result: [[1. 2.],[3. 4.]] | Pass |
| TC-A03 | test_empty_client_handling | Verify handling when no clients participate | Server running, no clients submitting updates | 1. Do not submit any client updates<br>2. Execute aggregation operation | No client updates | System maintains original parameters without error | No client updates, keeping original parameters | Pass |
| TC-A04 | test_weighted_aggregation | Verify weighted aggregation based on sample sizes | Server running, 3 clients submitting weighted models | 1. Client 1: value=1, sample size=50<br>2. Client 2: value=2, sample size=100<br>3. Client 3: value=3, sample size=150<br>4. Calculate weighted average | Weighted average formula: (1*50 + 2*100 + 3*150)/(50+100+150) | Weighted average = 2.333 | Expected weighted average: 2.3333333333333335<br>Actual aggregated value: 2.333333333333333 | Pass |
| TC-A05 | test_he_aggregation_structure | Verify homomorphic encryption configuration | Server configured with HE encryption | 1. Check HE encryption configuration<br>2. Verify encryption settings | HE encryption configuration | HE aggregation configuration correct | HE encryption ratio: 0.02<br>HE mask seed: 42 | Pass |
| TC-A06 | test_mad_reputation_aggregation | Verify MAD+Reputation defensive aggregation | Server running, 3 clients submitting models (including anomaly) | 1. Client 1: normal value 1.0<br>2. Client 2: normal value 2.0<br>3. Client 3: anomaly value 10.0<br>4. Execute defensive aggregation | Normal average: 1.5<br>Full average: 4.333 | Defensive aggregation result close to normal values (1.627) | Client 1: 1.0, Client 2: 2.0, Client 3: 10.0 (anomaly)<br>Defensive aggregation result: 1.6272842117423778<br>Reputation scores:<br>  Client 1: round_score=0.9447, trust=0.9834<br>  Client 2: round_score=1.0000, trust=1.0000<br>  Client 3: round_score=0.0263, trust=0.7079 | Pass |
| TC-A07 | test_trust_update | Verify trust score update | System records client historical behavior | 1. Client 3 submits anomaly value<br>2. Check trust score change | Initial trust: 1.0000 | Anomalous client trust decreased | Client 3 trust: 1.0000 → 0.8350 | Pass |

---

### C.4 Test Summary

| Test Module | Test Cases | Passed | Failed | Status |
|---|---|---|---|---|
| Model Type Testing | 4 | 4 | 0 | PASSED |
| Flower Communication Protocol Testing | 6 | 6 | 0 | PASSED |
| Model Aggregation Testing | 7 | 7 | 0 | PASSED |
| **Total** | **17** | **17** | **0** | **All tests passed** |

---

### C.5 Test Environment

| Item | Specification |
|---|---|
| **Operating System** | macOS |
| **Python Version** | 3.10 |
| **Test Date** | 2026-03-22 |
| **Test Framework** | Python unittest |
| **Federated Learning Framework** | Flower |
| **Machine Learning Library** | PyTorch (torchvision warning: missing libjpeg.9.dylib, ignored as image functionality not used) |
| **Numerical Computing Library** | NumPy |
| **Test Execution Environment** | FAIens conda environment (daixinchendeMacBook-Pro) |

---

### C.6 Test Execution Command & Output

```bash
# run all tests
python tests/run_all_tests.py

# run individual test
python tests/test_model_types.py
python tests/test_flower_protocol.py
python tests/test_model_aggregation.py