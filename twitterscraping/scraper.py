### Environment Setup ###

import os
import time
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
options = webdriver.ChromeOptions()
options.headless = False  # Disable headless mode for debugging

options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
options.add_argument("--incognito")

driver = webdriver.Chrome(options=options)
# List of OSINT organizations and sources
query_list = ["Trump", "DEI", "Russia", "border", "Ukraine", "immigration", "election", "asylum", "Palestine", "police"]

all_data = []


### Data Collection ###
# Search query template
for query in query_list:
    # Store results ("trump" OR "Trump" OR "Ukraine" OR "Russia" OR "economy" OR "vote" OR "election")
    data = []
    params = {
            "q": f'site:twitter.com inurl:/status/ -inurl:/HelpfulNotes/ "Readers added context" {query} after:{YEAR}-01-01 before:{YEAR}-12-31',
            "api_key": SERP_API_KEY,
            "engine": "google",
            "num": 100  # Get top 10 results per source
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
            filtered_element = " ".join(word for word in element.split() if ".com" not in word)
            if (element != "note found" and len(filtered_element) > 3):
                filtered_element = " ".join(word for word in element.split() if ".com" not in word)

                try:
                    response = requests.post(
                        "https://api.sapling.ai/api/v1/tone",
                        json={
                            "key": f"{TONE_API_KEY}",
                            "text": f"{filtered_element}"
                        }
                    )
                except Exception as e:
                    print(f'tone api error - {e}')
                    time.sleep(2 * 60)

                try:
                    if (response, response.json()):
                        if (len(response.json()["overall"]) < 1):
                            print(link, filtered_element, response, response.json())
                        responses[i] = response.json()["overall"][0][0]
                        responses[i+1] = response.json()["overall"][0][1]
                    i = i + 2
                except Exception as e:
                    print(f'error accessing response - {e}')
                    print(response, response.json())
                    if response.json()['msg'] == 'Rate Limited. Visit https://sapling.ai/docs/api/api-access for details.':
                        time.sleep(2 * 60)



        


        data.append([query, title, YEAR, link, elements[0], responses[0], responses[1], elements[1], responses[2], responses[3], elements[2], responses[4], responses[5]])
        all_data.append([query, title, YEAR, link, elements[0], responses[0], responses[1], elements[1], responses[2], responses[3], elements[2], responses[4], responses[5]])


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

    driver.delete_all_cookies()

full_df = pd.DataFrame(all_data, columns=["Query", "Title", "Year", "URL", "Tweet1", "Temp1", "Tone1", "Tweet2", "Temp2", "Tone2", "Note", "NoteTemp", "NoteTone"])
# Count word frequencies
full_tweet_word_counts = Counter(np.concatenate([full_df['Tone1'].dropna().to_numpy(), full_df['Tone2'].dropna().to_numpy()]))
full_note_word_counts = Counter(full_df['NoteTone'].dropna().to_numpy())

# create graph labels
full_tweet_labels = list(full_tweet_word_counts.keys())
full_note_labels = list(full_note_word_counts.keys())


# get graph values (integers)
full_tweet_values = list(full_tweet_word_counts.values()) # Corresponding counts
full_note_values = list(full_note_word_counts.values())
# Create bar graph
plt.figure(figsize=(8, 5))
plt.bar(full_tweet_labels, full_tweet_values, color='skyblue')

# Add labels and title
plt.xlabel("Tones")
plt.ylabel("Frequency")
plt.title("Tone Frequency Bar Chart")

# Show values on top of bars
for i, v in enumerate(full_tweet_values):
    plt.text(i, v + 0.1, str(v), ha='center', fontsize=12)

# Save the plot as a PNG file
plt.savefig(f"./files/bar/all_tweettone_frequency_bar_{YEAR}.png", format="png")

# repeat for note tone graph
plt.figure(figsize=(8, 5))
plt.bar(full_note_labels, full_note_values, color='red')

# Show values on top of bars
for i, v in enumerate(full_note_values):
    plt.text(i, v + 0.1, str(v), ha='center', fontsize=12)

# Save the plot as a PNG file
plt.savefig(f"./files/bar/all_notetone_frequency_bar_{YEAR}.png", format="png")

### Save Data ### 
full_df.to_csv(f"./files/csv/all_osint_reports_{YEAR}.csv", index=False)
full_df.to_excel(f"./files/excel/all_osint_reports_{YEAR}.xlsx", index=False)


print("✅ OSINT reports saved to files folder")

driver.quit()