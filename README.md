Output:
![Screenshot 2025-03-22 171523](https://github.com/user-attachments/assets/ad8b34b9-f211-4bbf-a7de-d349c7a55f31)
# Sentiment-Analysis-on-Reviews-of-Cosmetic-Products


This project focuses on web scraping product reviews from multiple e-commerce platforms (Amazon, Tira, and Smytten), performing sentiment analysis, and recommending the best platform based on the sentiment of the reviews. It also includes a web interface built with Flask for inputting product URLs and displaying results.

## Project Overview
The Web Scraping and Sentiment Analysis project collects product reviews using Selenium for automation and performs sentiment analysis using VADER to determine the polarity of customer feedback. The project aims to compare reviews from different platforms and recommend the best one based on sentiment.

## Features:

**Web Scraping:** Extracts reviews from multiple platforms.
**Sentiment Analysis:** Uses VADER sentiment analysis to determine positive, negative, or neutral reviews.
**Platform Comparison:** Compares sentiment scores and review counts across platforms and selects the best platform.
**Flask Integration:** Provides a user-friendly web interface for entering product URLs and displaying results.

## Technologies Used:

Python: Core programming language used for scraping and sentiment analysis.
Selenium: Automates web scraping of product reviews.
VADER Sentiment Analysis: An NLP tool used for sentiment classification.
Flask: Provides a web interface for easy user interaction.
Pandas: For data manipulation and analysis.
Matplotlib: Used for visualizing the review counts and sentiment scores.

## File Structure

- main.py # Flask application, Selenium and ML script
- templates/
  - index.html # HTML file for the web interface
- static/
  - img.png

## Usage
**Input the Product URLs:**
- Navigate to the Flask web interface.
- Input the product URLs from Amazon, Tira, and Smytten.
**Perform Sentiment Analysis:**
- The backend scrapes reviews from the provided URLs.
- VADER sentiment analysis is performed to categorize the reviews as positive, neutral, or negative.
**View Results:**
- The results show the number of reviews, average sentiment scores, and the platform with the best sentiment.
- A bar chart visualizing the review counts and sentiment scores is generated and displayed on the webpage.


## Future Improvements

- Add support for more e-commerce platforms.
- Improve the sentiment model by incorporating advanced NLP techniques.
- Implement user authentication for personalized recommendations.
- Enhance the Flask web interface with more detailed product comparisons.
  
**Contributions:**

Feel free to fork this repository and submit pull requests. Suggestions and improvements are always welcome!


  
