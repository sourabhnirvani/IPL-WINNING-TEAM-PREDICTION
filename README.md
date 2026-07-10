<div align="center">
  
  # 🏏 IPL Winning Team Prediction 🏆
  
  ![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
  ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
  ![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
  ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)

  **A Machine Learning based web application that predicts the winning probability of an IPL team in real-time during a match!** 🚀

</div>

---

## 🌟 Overview

Welcome to the **IPL Win Probability Predictor**! This application uses historical IPL match data to train a classification model that provides real-time win probabilities for both the chasing and defending teams based on the current match situation.

Whether you're a cricket enthusiast following a nail-biting run chase or a data science fan curious about predictive modeling, this tool gives you live statistical insights on the game! 📊

<br>

## ✨ Key Features

- ⚡ **Real-Time Predictions**: Input current match stats (score, overs, wickets, target) and get instant win probabilities.
- 🎨 **Interactive UI**: Built with Streamlit for a smooth, responsive, and user-friendly experience.
- 🤖 **Machine Learning Powered**: Uses a trained classification pipeline to accurately estimate win chances based on past IPL matches.
- 📈 **Dynamic Metrics**: Automatically calculates essential derived stats like Current Run Rate (CRR), Required Run Rate (RRR), Runs Left, and Balls Left.

<br>

## ⚙️ How It Works

The application requires the following inputs:
1. **Batting Team** 🏏
2. **Bowling Team** 🎯
3. **Host City** 🏟️
4. **Target Score** 🎯
5. **Current Score** 🏏
6. **Overs Completed** ⏱️
7. **Wickets Out** ❌

Using these inputs, the app calculates the match context and feeds the data into a pre-trained Machine Learning pipeline (`pipe.pkl`), which outputs the percentage probability of either team winning.

<br>

## 📁 Project Structure

```bash
📦 IPL-WINNING-TEAM-PREDICTION
 ┣ 📜 app.py                 # The main Streamlit web application
 ┣ 📜 train_model.py         # Script to train the ML model & generate pipe.pkl
 ┣ 📜 convert_cricsheet.py   # Script to parse & convert raw cricket data
 ┣ 📜 pipe.pkl               # Serialized ML pipeline (encoders + classifier)
 ┣ 📜 requirements.txt       # Python dependencies list
 ┗ 📜 README.md              # Project documentation
```

<br>

## 🚀 Installation Setup

> **Note:** For this project, please ensure you have **Python 3.8 to 3.13** installed on your system.

Follow these steps to get the project running on your local machine!

### 1️⃣ Clone the repository
```bash
git clone https://github.com/sourabhnirvani/IPL-WINNING-TEAM-PREDICTION.git
cd IPL-WINNING-TEAM-PREDICTION
```

### 2️⃣ Create a Virtual Environment (Recommended)
```bash
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate
```

### 3️⃣ Install Dependencies
Install the required Python packages using `pip`:
```bash
pip install -r requirements.txt
```

<br>

## 📦 Packages Used
This project relies on the following incredible open-source libraries:
- **[Streamlit](https://streamlit.io/)**: For building the beautiful web interface.
- **[Pandas](https://pandas.pydata.org/)**: For robust data manipulation and analysis.
- **[NumPy](https://numpy.org/)**: For fast numerical computations.
- **[Scikit-Learn](https://scikit-learn.org/)**: For the Machine Learning model and pipeline construction.

<br>

## 💻 Running the Application

To fire up the Streamlit app locally, execute the following command in your terminal:

```bash
streamlit run app.py
```

This will start a local web server. Open your browser and navigate to:
👉 **`http://localhost:8501/`**

<br>

---
<div align="center">
  <i>If you like this project, please consider giving it a ⭐ on GitHub!</i>
</div>
