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
    return total_sentiment_score / (len(reviews)+10) if reviews else 0 #weighted avg


# Function to scrape reviews from TIRA
# Function to scrape reviews from TIRA
def scrape_tira_reviews(url):
    driver = init_driver()
    driver.get(url)
    time.sleep(5)
    product_name = None
    try:
        # Extract product name
        product_name_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'product-title-container'))
        )
        product_name = product_name_element.text.strip()

        # Wait for review elements to be present
        reviews = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.tira-feedback-service-review-heading-secondary'))
        )
    except TimeoutException:
        print("TimeoutException: Could not find review elements or product name on the TIRA page.")
        driver.quit()
        return [], product_name
    review_texts = [review.text.strip() for review in reviews]
    driver.quit()
    return review_texts, product_name



# Function to scrape reviews from Amazon

def scrape_amazon_reviews(url):
    driver = webdriver.Edge()  # Initialize your driver (adjust the path if necessary)
    driver.get(url)
    all_reviews = []

    try:
        product_name = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'titleSection'))
        ).text.strip()
        # Increase wait time for the "See all reviews" button
        WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@data-hook, 'see-all-reviews-link-foot')]"))
        )

        # Click "See all reviews" button
        see_all_reviews_button = driver.find_element(By.XPATH, "//a[contains(@data-hook, 'see-all-reviews-link-foot')]")
        see_all_reviews_button.click()
        time.sleep(5)

        # Loop through review pages
        pagination_attempts = 20
        for _ in range(pagination_attempts):
            # Scroll to the bottom to load more reviews if necessary
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            # Collect reviews
            reviews = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, "//span[@data-hook='review-body']"))
            )
            for review in reviews:
                all_reviews.append(review.text.strip())

            # Check for "Next Page" button
            try:
                next_page_button = driver.find_element(By.CLASS_NAME, 'a-last')
                if "a-disabled" in next_page_button.get_attribute("class"):
                    print("Reached the last page of reviews.")
                    break
                next_page_button.click()
                time.sleep(5)
            except Exception as e:
                print(f"Pagination error or end of pages reached: {e}")
                break
    except TimeoutException:
        print("TimeoutException: Could not find review elements or 'See all reviews' button on the Amazon page.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        driver.quit()
    return all_reviews,product_name

# Function to scrape reviews from Smytten
def scrape_smytten_reviews(url):
    driver = init_driver()
    driver.get(url)
    time.sleep(5)
    try:
        div_name = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'css-bfy7gq'))
        ).text.strip()
        h1_name = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'css-pbjvln'))
        ).text.strip()
        product_name = f"{div_name} {h1_name}"
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
    return review_texts, product_name


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
    tira_reviews, tira_product_name = scrape_tira_reviews(tira_url)
    tira_average_score = calculate_average_sentiment(tira_reviews) if tira_reviews else 0

    amazon_reviews, amazon_product_name = scrape_amazon_reviews(amazon_url)
    amazon_average_score = calculate_average_sentiment(amazon_reviews) if amazon_reviews else 0

    smytten_reviews, smytten_product_name = scrape_smytten_reviews(smytten_url)
    smytten_average_score = calculate_average_sentiment(smytten_reviews) if smytten_reviews else 0

    # Determine the best platform
    scores = {
        'TIRA': tira_average_score,
        'Amazon': amazon_average_score,
        'Smytten': smytten_average_score
    }
    #best_platform = max(scores, key=scores.get)
    max_score = max(scores.values())

    # Find all platforms with the maximum score
    best_platform = [platform for platform, score in scores.items() if score == max_score]


    if len(best_platform) == 1:
        best_platform = best_platform[0]
    elif len(best_platform) == 2:
        best_platform = f"Both {best_platform[0]} and {best_platform[1]} are good"
    elif len(best_platform) == 3:
        best_platform = "All platforms are equally good"

    return jsonify({
        'best_platform': best_platform,
        'tira_product_name': tira_product_name,
        'tira_average_score': tira_average_score,
        'tira_reviews_count': len(tira_reviews),
        'amazon_product_name': amazon_product_name,
        'amazon_average_score': amazon_average_score,
        'amazon_reviews_count': len(amazon_reviews),
        'smytten_product_name': smytten_product_name,
        'smytten_average_score': smytten_average_score,
        'smytten_reviews_count': len(smytten_reviews)
    })


if __name__ == '__main__':
    app.run(debug=True, port=5001)

#https://www.tirabeauty.com/product/maybelline-new-york-super-stay-up-to-30h-lumi-matte-foundation-spf-16-pa-220-35-ml-7592551
#https://www.amazon.in/Lovechild-Masaba-Everything-Blurring-Technology/dp/B0D499R7F4?th=1
#https://smytten.com/trial/product/foundation/bb-foundation-spf-15-medium-beige-02/DINC0068BB1