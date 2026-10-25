# SafeNova - Technical Design Document

## 1. Project Overview

SafeNova is an AI and GIS-based prototype designed to identify possible construction changes and help authorities prioritize inspections.

The system flags suspicious changes for human verification. It does not automatically determine whether a building is illegal.

## 2. Problem Statement

Manual monitoring of construction activities can be time-consuming. SafeNova aims to support monitoring by comparing images, visualizing possible changes, and displaying their locations on a GIS map.

## 3. System Architecture

Step 1: Collect earlier and recent images.

Step 2: Preprocess the images.

Step 3: Compare the images to identify possible changes.

Step 4: Display potential alerts.

Step 5: Show the locations on a GIS map.

Step 6: Allow authorized officers to verify the alerts.

Step 7: Make decisions only after verification.

## 4. Technologies Used

- Python
- Streamlit
- NumPy
- Pillow
- Folium
- Pandas

## 5. Prototype Workflow

1. The user uploads an earlier image and a recent image.
2. The prototype compares the images to highlight pixel differences.
3. It displays an approximate change percentage.
4. Sample locations are displayed on a GIS map.
5. An authorized officer verifies any real alert using appropriate evidence and approval records.

## 6. Limitations

The initial prototype uses basic pixel comparison, not a trained AI model. Changes in lighting, weather, seasons, and camera angles can cause false alerts. The sample map records are fictional.

## 7. Future Enhancements

- Develop a trained AI-based building change-detection model.
- Integrate legally obtained satellite or drone imagery.
- Add authorized building approval records.
- Improve GIS visualization and alert prioritization.
- Evaluate accuracy and false-positive rates.

## 8. Responsible Use

SafeNova is a student prototype. Its alerts must not be treated as proof of unauthorized construction. Human verification is required before any official action.
