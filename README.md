# IPL Winning Team Prediction

This is a Machine Learning based web application that predicts the winning probability of an IPL team during a match. The app uses historical IPL match data to train a model and provides real-time win probabilities for the chasing team and the defending team based on the current match situation.

## Features
- **Real-Time Predictions**: Input current match stats (score, overs, wickets, target) to get instant win probabilities.
- **Interactive UI**: Built with Streamlit for a smooth and user-friendly experience.
- **Machine Learning**: Uses a trained classification model to accurately estimate win chances based on past IPL matches.

## How It Works
The application takes the following inputs:
- Batting Team
- Bowling Team
- Host City
- Target Score
- Current Score
- Overs Completed
- Wickets Out

Using these inputs, it calculates the runs left, balls left, current run rate (CRR), and required run rate (RRR). These derived features are then fed into a pre-trained Machine Learning pipeline (`pipe.pkl`) which outputs the probability of the batting team winning and the bowling team winning.

## Project Structure
- `app.py`: The main Streamlit web application.
- `train_model.py`: Script used to train the machine learning model and generate `pipe.pkl`.
- `convert_cricsheet.py`: Script to parse and convert raw cricket data (Cricsheet JSON/YAML) into CSV format.
- `pipe.pkl`: The serialized Machine Learning pipeline (including encoders and the classifier).
- `requirements.txt`: List of Python dependencies required to run the project.

## Installation Setup

Follow these steps to get the project running on your local machine:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sourabhnirvani/IPL-WINNING-TEAM-PREDICTION.git
   cd IPL-WINNING-TEAM-PREDICTION
   ```

2. **Create a Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   Install the required Python packages using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

## Packages to Install
The project requires the following primary packages (listed in `requirements.txt`):
- `streamlit`: For building the web interface.
- `pandas`: For data manipulation and analysis.
- `numpy`: For numerical computations.
- `scikit-learn`: For the Machine Learning model and pipeline.

## Running the Application

To run the Streamlit app locally, execute the following command in your terminal:

```bash
streamlit run app.py
```

This will start a local web server, and you can view the application in your browser at `http://localhost:8501/`.
