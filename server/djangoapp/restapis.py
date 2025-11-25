# Uncomment the imports below before you add the function code
import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")


def get_request_custom(endpoint, **kwargs):
    params = ""
    if kwargs:
        for key, value in kwargs.items():
            params = params + key + "=" + value + "&"
    request_url = backend_url + endpoint + "?" + params
    print("GET from {} ".format(request_url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        json_data = response.json()
        # Check if the response is a string instead of a dict/list
        if isinstance(json_data, str):
            raise Exception("Invalid response: " + json_data)
        return json_data
    except Exception:
        # If any error occurs
        print("Network exception occurred")
        # Fallback to mock data
        try:
            from django.conf import settings
            import json

            json_path = settings.BASE_DIR / 'database/data'

            if "/fetchDealers" in endpoint:
                with open(json_path / 'dealerships.json', 'r') as f:
                    data = json.load(f)
                    dealers = data['dealerships']

               if ("/fetchDealers/" in endpoint and
                        endpoint != "/fetchDealers"):
                    state = endpoint.split("/fetchDealers/")[1]
                    return [d for d in dealers if d['state'] == state]
                return dealers

            if "/fetchReviews" in endpoint:
                with open(json_path / 'reviews.json', 'r') as f:
                    data = json.load(f)
                    reviews = data['reviews']

                if "/dealer/" in endpoint:
                    dealer_id = int(endpoint.split("/dealer/")[1])
                    return [r for r in reviews if r['dealership'] == dealer_id]
                return reviews

            if "/fetchDealer/" in endpoint:
                with open(json_path / 'dealerships.json', 'r') as f:
                    data = json.load(f)
                    dealers = data['dealerships']
                dealer_id = int(endpoint.split("/fetchDealer/")[1])
                for d in dealers:
                    if d['id'] == dealer_id:
                        return d
        except Exception as e:
            print(f"Mock data error: {e}")
        return None


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + "analyze/" + text
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        return response.json()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")


def post_review(data_dict):
    request_url = backend_url + "/insert_review"
    try:
        response = requests.post(request_url, json=data_dict)
        print(response.json())
        json_data = response.json()
        if isinstance(json_data, str):
            raise Exception("Invalid response: " + json_data)
        return json_data
    except Exception:
        print("Network exception occurred")
        # Fallback to mock data
        try:
            from django.conf import settings
            import json

            json_path = settings.BASE_DIR / 'database/data'
            with open(json_path / 'reviews.json', 'r') as f:
                data = json.load(f)

            reviews = data['reviews']
            # Generate new ID
            new_id = reviews[-1]['id'] + 1 if reviews else 1

            # Create new review object
            new_review = data_dict.copy()
            new_review['id'] = new_id
            new_review['purchase'] = new_review.get('purchase', False)
            new_review['purchase_date'] = new_review.get('purchase_date', "")
            new_review['car_make'] = new_review.get('car_make', "")
            new_review['car_model'] = new_review.get('car_model', "")
            new_review['car_year'] = new_review.get('car_year', "")

            reviews.append(new_review)
            data['reviews'] = reviews

            with open(json_path / 'reviews.json', 'w') as f:
                json.dump(data, f, indent=2)

            return new_review
        except Exception as e:
            print(f"Mock data write error: {e}")
            return None
