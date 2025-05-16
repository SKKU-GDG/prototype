# GAP EAR App Prototype 

## Introduction

This application is a prototype app that analyzes the difference between a sentence entered by the user and the sentence recognized through Google Cloud STT (Speech-to-Text) using the Gemini API. Based on this analysis, it provides feedback to the user. Through this app, users can visually identify the discrepancies between their actual pronunciation and the speech recognition results, gaining insights for improvement.

This app is designed to provide an early experience of the core functionalities of the GAP EAR app.

## Key Features

1.  **Sentence Input:** Allows users to input sentences in text form.
2.  **Speech Recognition:** Performs speech recognition on the entered sentence using Google Cloud STT.
3.  **Difference Analysis:** Analyzes the differences between the originally entered sentence and the recognized sentence using the Gemini API.
4.  **Feedback Provision:** Provides users with feedback for improving their pronunciation and speech recognition based on the analysis results.

## About the GAP EAR App

GAP EAR aims to help users reduce the 'gap' between their pronunciation and the actual pronunciation, enabling more accurate and natural speech. This prototype app allows you to experience the core concept of GAP EAR.

## Technology Stack

The application is developed using the following technology stack:

### Frontend

* **HTML:** Defines the structure of the user interface.
* **CSS:** Handles the styling and layout of the user interface.
* **JavaScript:** Manages user interactions and dynamic functionalities.

### Backend

* **Flask:** A Python-based micro web framework used to implement the server-side logic.
* **Google Cloud STT:** Provides the speech recognition capabilities.
* **Gemini API:** Used to analyze the differences between sentences and generate feedback.

### Deployment

* **Render:** Deployed via Render, a cloud-based web application deployment platform (free instance).

## How to Run (Render Environment)

This app is deployed through a free instance on Render, so you can experience it directly without any local environment setup via the link below:

[https://prototype-hiwo.onrender.com/](https://prototype-hiwo.onrender.com/)
