### Environment Setup ###

import os
import pandas as pd
import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

# from wordcloud import WordCloud, STOPWORDS

# Add custom stopwords
# custom_stopwords = STOPWORDS.union({"https", "s", "//", "x", "twitter"})


# Load API key from .env file
load_dotenv()
SERP_API_KEY = os.getenv("SERP_API_KEY")
TONE_API_KEY = os.getenv("TONE_API_KEY")

YEAR = 2024

# Check if the API key is loaded
if not SERP_API_KEY:
    raise ValueError("⚠ ERROR: API Key not found. Make sure it's in the .env file!")
# Set up Selenium WebDriver (make sure to have ChromeDriver installed)
driver = webdriver.Chrome()
# List of OSINT organizations and sources
# sources = {
#     "Bellingcat": "site:bellingcat.com",
#     "DFRLab (Atlantic Council)": "site:atlanticcouncil.org",
#     "EU DisinfoLab": "site:disinfo.eu",
#     "Graphika": "site:graphika.com",
#     "NATO StratCom COE": "site:stratcomcoe.org",
#     "RAND Corporation": "site:rand.org",
#     "BBC Monitoring": "site:bbc.com/news",
#     "OSINT Foundation": "site:osintfoundation.com",
#     "Oxford Internet Institute": "site:oii.ox.ac.uk",
#     "Global Engagement Center (US Gov)": "site:state.gov/gec"
# }

### Data Collection ###
# Search query template
query = 'Palestine'

# Store results ("trump" OR "Trump" OR "Ukraine" OR "Russia" OR "economy" OR "vote" OR "election")
data = []
params = {
        "q": f'site:twitter.com inurl:/status/ -inurl:/HelpfulNotes/ "Readers added context" {query} after:{YEAR}-01-01 before:{YEAR}-12-31',
        "api_key": SERP_API_KEY,
        "engine": "google",
        "num": 10  # Get top 10 results per source
    }
search = GoogleSearch(params)
results = search.get_dict()
for result in results.get("organic_results", []):
    title = result.get("title", "No Title")
    link = result.get("link", "No Link")
    headers = {"User-Agent": "Mozilla/5.0"}
    driver.get(link)
    try:
        tweet_text_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="tweetText"]'))
        )

        notes = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="birdwatch-pivot"]'))
        )
    except:
        print("not a tweet")
        continue

    l = len(tweet_text_elements)
    elements = ["n/a", "n/a", "n/a"]
    elements[0] = tweet_text_elements[0].text
    elements[1] = ''
    if (l > 1):
        elements[1] = tweet_text_elements[1].text


    note_text = notes[0].text.replace("Readers added context they thought people might want to know\n", "")
    elements[2] = note_text

    responses = ["n/a", "sweet", "n/a", "sweet", "n/a", "bad"]
    i = 0

    for element in elements:
        if (element != "note found" and len(element) > 3):
            response = requests.post(
                "https://api.sapling.ai/api/v1/tone",
                json={
                    "key": f"{TONE_API_KEY}",
                    "text": f"{element}"
                }
            )

            if (response.json and response.json()["overall"]):
                responses[i] = response.json()["overall"][0][0]
                responses[i+1] = response.json()["overall"][0][1]
            i = i + 2


    


    data.append([query, title, YEAR, link, elements[0], responses[0], responses[1], elements[1], responses[2], responses[3], elements[2], responses[4], responses[5]])


### Data Processing/Analysis ###

# Convert to DataFrame
df = pd.DataFrame(data, columns=[f"{query}", "Title", "Year", "URL", "Tweet1", "Temp1", "Tone1", "Tweet2", "Temp2", "Tone2", "Note", "NoteTemp", "NoteTone"])

# Count word frequencies
tweet_word_counts = Counter(np.concatenate([df['Tone1'].dropna().to_numpy(), df['Tone2'].dropna().to_numpy()]))
note_word_counts = Counter(df['NoteTone'].dropna().to_numpy())

# create graph labels
tweet_labels = list(tweet_word_counts.keys())
note_labels = list(note_word_counts.keys())
# List of all possible tones
# labels = list([
#     "admiring",
#     "amused",
#     "angry",
#     "annoyed",
#     "approving",
#     "aware",
#     "confident",
#     "confused",
#     "curious",
#     "eager",
#     "disappointed",
#     "disapproving",
#     "embarassed",
#     "excited",
#     "fearful",
#     "grateful",
#     "joyful",
#     "loving",
#     "mournful",
#     "neutral",
#     "optimistic",
#     "relieved",
#     "remorseful",
#     "repulsed",
#     "sad",
#     "worried",
#     "surprised",
#     "sympathetic"
#     ]
# )

# get graph values (integers)
tweet_values = list(tweet_word_counts.values()) # Corresponding counts
note_values = list(note_word_counts.values())
# Create bar graph
plt.figure(figsize=(8, 5))
plt.bar(tweet_labels, tweet_values, color='skyblue')

# Add labels and title
plt.xlabel("Tones")
plt.ylabel("Frequency")
plt.title("Tone Frequency Bar Chart")

# Show values on top of bars
for i, v in enumerate(tweet_values):
    plt.text(i, v + 0.1, str(v), ha='center', fontsize=12)

# Save the plot as a PNG file
plt.savefig(f"./files/bar/{query}_tweettone_frequency_bar_{YEAR}.png", format="png")

# repeat for note tone graph
plt.figure(figsize=(8, 5))
plt.bar(note_labels, note_values, color='red')

# Show values on top of bars
for i, v in enumerate(note_values):
    plt.text(i, v + 0.1, str(v), ha='center', fontsize=12)

# Save the plot as a PNG file
plt.savefig(f"./files/bar/{query}_notetone_frequency_bar_{YEAR}.png", format="png")


# Create Wordclouds if necessary

# combined_tweets = df['Tweet1'] + " " + df['Tweet2']
# combined_tone = 


# tweet_cloud_text = "".join(combined_tweets.dropna())
# tweet_wordcloud = WordCloud(stopwords=custom_stopwords, width=1600, height=800, background_color="white").generate(tweet_cloud_text)
# tweet_wordcloud.to_file(f"./files/wordcloud/{query}_tweets_wordcloud.png")

# tweet_tone_words = "".join(combined_tone.dropna())
# tweet_tone_wordcloud = WordCloud(stopwords=custom_stopwords, width=1600, height=800, background_color="white").generate(tweet_tone_words)
# tweet_tone_wordcloud.to_file(f"./files/wordcloud/{query}_tweettone_wordcloud.png")

# note_cloud_text = "".join(df["NoteTone"].dropna())
# note_wordcloud = WordCloud(stopwords=custom_stopwords, width=1600, height=800, background_color="white").generate(note_cloud_text)
# tweet_wordcloud.to_file(f"./files/wordcloud/{query}_notetone_wordcloud.png")

### Save Data ### 
df.to_csv(f"./files/csv/{query}_osint_reports_{YEAR}.csv", index=False)
df.to_excel(f"./files/excel/{query}_osint_reports_{YEAR}.xlsx", index=False)

print("✅ OSINT reports saved to files folder")

driver.quit()