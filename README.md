# Toxicity-Moderated Snake & Ladders (with Reinforcement Learning)

A 4-player Snake & Ladders game with chat moderation.  
Messages are analyzed for toxicity using a model trained on the Kaggle dataset `uetchy/sensai`,  
and an RL agent decides whether to allow, warn, or kick a player.

## How to run

1. Create a virtual environment:
    python -m venv .venv
    .\.venv\Scripts\activate
2. Install dependencies:
    pip install -r requirements.txt
3. Train the model:
    python src\data\prepare_dataset.py --source kaggle --kaggle-id uetchy/sensai
4. Run the game:
    python src\app.py
Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

