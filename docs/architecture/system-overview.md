
# System Overview

## Project Description

This project implements a Federated Learning image classification system using the Flower framework.

The objective is to enable multiple clients to collaboratively train a machine learning model without directly sharing their local datasets, improving privacy while maintaining model performance.

The system integrates three key research areas:

- Federated Learning
- Privacy Preservation
- Robustness Against Malicious Participants

---

## Core Components

### Client Layer

Each client:

- Holds local training data
- Trains a local model independently
- Sends model updates to the server
- Never shares raw training data

---

### Federated Server

The server:

- Coordinates training rounds
- Aggregates model parameters
- Distributes updated global models
- Evaluates training progress

---

### Privacy Module

Privacy-preserving mechanisms include:

- Homomorphic Encryption
- Secure parameter exchange
- Encrypted aggregation workflow

---

### Robustness Module

Robustness features include:

- Detection of malicious model updates
- Aggregation defenses
- Attack simulation testing

---

### Availability Module

Availability testing includes:

- Random client disconnections
- Partial participation scenarios
- Federated training continuity analysis

---

## Technology Stack

### Machine Learning

- PyTorch

### Federated Learning

- Flower Framework

### Backend

- Python

### Data

- MNIST Dataset

### Visualization

- Matplotlib

### Frontend Interface

- HTML
- CSS
- JavaScript

---

## Project Structure

GRPSoftware.Team202518

├── back_end/
├── static/
├── templates/
├── tests/
├── image_folder/
├── app.py
├── Simulator.py
└── README.md

---

## Research Objectives

The project evaluates:

- Model performance under federated learning
- Privacy-preserving training techniques
- Robustness against adversarial clients
- System reliability under node failures

---

## Educational Purpose

This project was developed as part of a Software Engineering Group Project at the University of Nottingham Ningbo China.
