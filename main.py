from flask import Flask, request, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import time

app = Flask(__name__)

# Initialize VADER sentiment analyzer
sia = SentimentIntensityAnalyzer()


# Initialize WebDriver
def init_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    driver_path = "C:/Users/valle/Downloads/edgedriver_win64/msedgedriver.exe"  # Update this path as needed
    driver = webdriver.Edge(options=options)
    return driver


# Function to calculate average sentiment score
def calculate_average_sentiment(reviews):
    total_sentiment_score = 0
    for review in reviews:
        sentiment_score = sia.polarity_scores(review)
        total_sentiment_score += sentiment_score['compound']
    return total_sentiment_score / len(reviews) if reviews else 0


# Function to scrape reviews from TIRA
def scrape_tira_reviews(url):
    driver = init_driver()
    driver.get(url)
    time.sleep(5)
    try:
        # Wait for review elements to be present
        reviews = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.tira-feedback-service-review-heading-secondary'))
        )
    except TimeoutException:
        print("TimeoutException: Could not find review elements on the TIRA page.")
        driver.quit()
        return []
    review_texts = [review.text.strip() for review in reviews]
    driver.quit()
    return review_texts


# Function to scrape reviews from Amazon
# Function to scrape reviews from Amazon
def scrape_amazon_reviews(url):
    driver = init_driver()
    driver.get(url)
    time.sleep(5)
    all_reviews = []
    try:
        # Click "See all reviews" button if present to navigate to the review page
        see_all_reviews_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@data-hook, 'see-all-reviews-link-foot')]"))
        )
        see_all_reviews_button.click()
        time.sleep(5)

        # Loop through pages and collect reviews
        pagination_attempts = 20  # Increase the number of pages to try and extract reviews from
        for _ in range(pagination_attempts):
            # Wait for reviews to load on the page
            reviews = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, "//span[@data-hook='review-body']"))
            )
            # Extract and store each review text
            for review in reviews:
                review_text = review.text.strip()
                all_reviews.append(review_text)

            # Check if the "Next Page" button is present and enabled
            try:
                next_page_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'a-last'))
                )
                if "a-disabled" in next_page_button.get_attribute("class"):
                    print("Reached the last page of reviews.")
                    break
                next_page_button.click()  # Click the "Next Page" button
                time.sleep(5)  # Adjust time to allow page to load before the next iteration
            except Exception as e:
                print(f"Pagination Error: {e}")
                break
    except TimeoutException:
        print("TimeoutException: Could not find review elements or 'See all reviews' button on the Amazon page.")
    except Exception as e:
        print(f"Unexpected error while scraping Amazon reviews: {e}")
    finally:
        driver.quit()  # Ensure the driver is closed in case of an error
    return all_reviews


# Function to scrape reviews from Smytten
def scrape_smytten_reviews(url):
    driver = init_driver()
    driver.get(url)
    time.sleep(5)
    try:
        # Scroll and load more reviews
        def load_more_reviews():
            scrollable_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "infinite-scroll-component"))
            )
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(3)

        for _ in range(5):  # Adjust range as needed
            load_more_reviews()

        # Wait for review elements to be present
        reviews = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-cmmjkl'))
        )
    except TimeoutException:
        print("TimeoutException: Could not find review elements on the Smytten page.")
        driver.quit()
        return []
    review_texts = [review.text.strip() for review in reviews]
    driver.quit()
    return review_texts


# Flask route for the home page
@app.route('/')
def home():
    return render_template('index.html')


# Flask route for comparing reviews
@app.route('/compare', methods=['POST'])
def compare_reviews():
    tira_url = request.form.get('tira_url')
    amazon_url = request.form.get('amazon_url')
    smytten_url = request.form.get('smytten_url')

    # Scrape reviews and calculate average sentiment scores
    tira_reviews = scrape_tira_reviews(tira_url)
    tira_average_score = calculate_average_sentiment(tira_reviews) if tira_reviews else 0

    amazon_reviews = scrape_amazon_reviews(amazon_url)
    amazon_average_score = calculate_average_sentiment(amazon_reviews) if amazon_reviews else 0

    smytten_reviews = scrape_smytten_reviews(smytten_url)
    smytten_average_score = calculate_average_sentiment(smytten_reviews) if smytten_reviews else 0

    # Determine the best platform
    scores = {
        'TIRA': tira_average_score,
        'Amazon': amazon_average_score,
        'Smytten': smytten_average_score
    }
    best_platform = max(scores, key=scores.get)

    return jsonify({
        'Best_platform': best_platform,
        'tira_average_score': tira_average_score,
        #'tira_reviews_count': len(tira_reviews),
        'amazon_average_score': amazon_average_score,
        #'amazon_reviews_count': len(amazon_reviews),
        'smytten_average_score': smytten_average_score,
        #'smytten_reviews_count': len(smytten_reviews)
    })


if __name__ == '__main__':
    app.run(debug=True, port=5001)
