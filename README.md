# Smart Campus Simulation
### A Miniature Cyber-Physical Red–Blue Team Environment
### Overview

The Smart Campus Simulation is a miniature model of a connected campus where multiple IoT zones are controlled and monitored through a central Raspberry Pi.
It demonstrates how a modern IoT-driven campus can be operated, attacked, and defended.

### The repository contains:

- ESP Tester Dashboard – main dashboard used to control campus LEDs, sensors, and zone behaviors.

- Red Team Attack Dashboard – interface to simulate attacks on the campus network.

- Blue Team Defence Dashboard – interface to monitor threats, anomalies, and campus health.

- This project was developed to visualize real-world cyber-physical interactions using IoT devices in a controlled academic environment.

Project Structure (High-Level)
/ESP-Tester-Dashboard
/Red-Team-Attack-Dashboard
/Blue-Team-Defence-Dashboard
/ESP32-Nodes
/Raspberry-Pi-Core
/Docs


####Each folder corresponds to one subsystem of the simulation.
Campus Zones
The campus is divided into four ESP32-powered zones:

- Building A
- Building B
- Parking Lot
- Park Zone

A Raspberry Pi acts as the main coordinator for the entire campus.
Based on the campus outline referenced in the introduction pages of the report 
, each zone communicates only with the Pi through a controlled virtual network.

## Dashboards
- ESP Tester Dashboard
  - Used by campus operators to:
  - Control LEDs and basic campus devices
  - View simplified sensor states
  - Trigger manual overrides

- Red Team Dashboard
  - Used to demonstrate offensive cybersecurity behavior:
  - Launch simulated attacks
  - Trigger malicious traffic
  - Stress-test connectivity and campus behavior
  - This mirrors the attacker panel described in the implementation section of the report 

- Blue Team Dashboard
  - Used to visualize defence operations:
  - Track suspicious activity
  - Observe system alerts
  - View basic logs and anomalies
  - This aligns with the defence dashboard description in the PDF, showing packet tracking and alerts 


Architectural Flowcharts
1. High-Level System Overview

(Interpreted from the architecture diagrams on pages 7–8 of the PDF 

)

      +---------------------+
      |   Campus Devices   |
      | (ESP32 - 4 Zones)  |
      +---------+-----------+
                |
                | Sensor & Control Data
                |
      +---------v------------+
      |   Raspberry Pi Core  |
      |  (Controller Layer)  |
      +----+---------+-------+
           |         |
           |         |
  +--------v--+   +--v---------+
  | Blue Team |   |  Red Team  |
  | Dashboard |   | Dashboard  |
  +-----------+   +------------+

2. Virtual Network & Device Flow

(Based on the system flow in the presentation pages 7–8 

)

      [ESP32 - A] ----\
      [ESP32 - B] -----\ 
      [ESP32 - Parking] ---->  (Virtual Wi-Fi Network) ---> [Router Layer] ---> [Raspberry Pi]
      [ESP32 - Park ] ----/

                                       |
                                       | Visualization & Operations
                                       |
                        +---------------------------+
                        | ESP Tester (User)        |
                        | Blue Team Dashboard      |
                        | Red Team Dashboard       |
                        +---------------------------+

3. Campus Hardware Layout

(Translated from the diagrams of campus zones spanning the project introduction Œintroduction pages

)

           [Building A - ESP32]
                    |
                    |
[Park Zone - ESP32] |     [Raspberry Pi Core]
                    |             |
                    |             |
           [Building B - ESP32]   |
                                  |
                         [Parking Zone - ESP32]

Purpose

The project highlights three core themes:

1. Operation

How a centralized dashboard can control a distributed IoT campus.

2. Offense

How IoT devices can be targeted through simulated red-team strategies, as described in the attack section of the PDF 

.

3. Defence

How a monitoring dashboard can detect unusual activity and alert the operator, corresponding to the defence section in the report.

Repository Usage

This repository is organized for academic demonstration.
Each folder contains assets for:

Running the dashboards

Viewing the campus model structure

Understanding subsystem separation

No sensitive or low-level technical details are exposed; only conceptual flow and operational behavior are included.
