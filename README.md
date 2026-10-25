# SafeNova-AI-GIS-Construction-Monitoring
AI-powered construction change detection and GIS-based monitoring system to identify potentially unauthorized construction and support faster municipal verification in Tamil Nadu.
# SafeNova – AI & GIS Construction Monitoring

## 1. Project Overview

SafeNova is a proposed AI- and GIS-based system to identify potentially unauthorized construction by analyzing changes in construction imagery and comparing them with available building approval records.

The system aims to support municipal authorities in Tamil Nadu by highlighting suspicious locations for further verification.

## 2. Problem Statement

Rapid urbanization makes construction monitoring challenging. Manual inspections, limited manpower, delayed detection, and scattered approval records can make it difficult for authorities to identify potentially unauthorized construction in time.

## 3. Proposed Solution

SafeNova proposes an integrated monitoring workflow using:

- AI-based construction change detection.
- Satellite or drone imagery, where available.
- GIS-based location mapping.
- Comparison with available building approval records.
- Risk-level alerts to prioritize field inspections.
- Human verification by authorized officials.

**Important:** An alert indicates a location requiring verification; it does not independently establish that a building is illegal.

## 4. Key Features (Planned)

- Before-and-after construction imagery comparison.
- Identification of potential construction changes.
- GIS dashboard for displaying flagged locations.
- Comparison with available approval information.
- Low, Medium, and High priority alerts.
- Support for municipal field verification.

These features are proposed and will be implemented and tested progressively.

## 5. Technology Stack (Proposed)

- Programming: Python
- AI / Computer Vision: OpenCV and suitable image-analysis models
- GIS: GeoPandas and Folium
- Data Processing: Pandas
- Interface: Streamlit (planned)

The final technology stack may change during development.

## 6. Getting Started

### Prerequisites

- Python 3.10 or a compatible version
- Git
- A code editor such as Visual Studio Code

### Current Repository Status

This repository currently contains the initial project description. The executable prototype, dependencies, and environment configuration are not yet available.

Setup and execution instructions will be added after the prototype is implemented.

## 7. Sample Data and Testing

Sample construction records and test cases will be added for demonstration and validation. Any synthetic data will be clearly labelled as demonstration data and will not represent official municipal records.

## 8. Technical Documentation

The system architecture, data flow, AI processing approach, GIS integration, and testing methodology will be documented in `TECHNICAL_DESIGN.md`.

## 9. Expected Impact

- Earlier identification of potential construction changes.
- Reduced dependence on routine manual screening.
- Better prioritization of municipal inspections.
- Improved support for transparent and sustainable urban planning.

## 10. Sustainable Development Goals

- SDG 11: Sustainable Cities and Communities.
- SDG 16: Peace, Justice and Strong Institutions.

## 11. License

An open-source license will be added after confirming the project code and third-party component licensing.

## Installation and Setup

### Requirements
- Python 3.10 or later
- Git
- Internet connection for installing dependencies and displaying map tiles

### Steps to Run

1. Clone the repository:

   `git clone https://github.com/swetha215swea-droid/SafeNova-AI-GIS-Construction-Monitoring.git`

2. Open the project folder:

   `cd SafeNova-AI-GIS-Construction-Monitoring`

3. Install the required packages:

   `pip install -r requirements.txt`

4. Start the application:

   `streamlit run app.py`

5. Open the local URL shown in the terminal.

## Features

- Compare earlier and recent construction images.
- Display approximate pixel differences.
- Visualize fictional sample alerts on a GIS map.
- View sample alert records.

## Technical Limitations

The current version uses basic image comparison. It does not yet contain a trained AI model or a verified connection to official building approval records. All sample alerts are illustrative and require human verification.

## Testing

Automated tests are planned. The application should be tested with sample images and checked for errors before demonstration.

## License

This project is released under the MIT License. See the `LICENSE` file for details.

## 12. Project Status

**Stage:** Initial concept and documentation.

**Next milestone:** Develop and test a basic working prototype using clearly labelled sample data.
