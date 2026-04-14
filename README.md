# Social Media Moderation Analytics

A Python data analysis project that processes and analyses social media 
moderation effectiveness across four datasets containing 800 users, 
2,500 posts, and 10,000 interactions.

## Project Overview

This project was built as part of an MSc in Computer Science & AI at the 
University of York. It demonstrates end-to-end data pipeline skills including 
cleaning, transformation, analysis and visualisation.

## Tech Stack

- Python 3.12
- pandas — data cleaning, merging, pivoting, groupby
- NumPy — numerical operations
- matplotlib & seaborn — visualisations
- Tkinter — interactive GUI
- JSON — data persistence and backup

## What It Does

- Loads and cleans four real-world style CSV datasets
- Excludes bot accounts from all human behaviour analysis
- Translates CSV data to a nested JSON structure
- Analyses report patterns by topic category and moderation level
- Pivots posting activity by hour of day and topic
- Performs categorical analysis across account type, content type and moderation level
- Produces correlation visualisations between moderation level and report frequency
- Maintains a complete audit log of all transformations
- Provides an interactive Tkinter GUI for stats and data exploration

## How to Run

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Add the four CSV files to the `data/` folder
4. Open `social_media_analytics.ipynb` in Jupyter and run all cells
5. Run `python gui.py` for the interactive GUI

## Dataset

The dataset is not included in this repository. It contains:
- `USERS.csv` — 800 user profiles
- `POSTS.csv` — 2,500 posts
- `INTERACTIONS.csv` — 10,000 engagement records
- `TOPICS.csv` — 8 topic categories
