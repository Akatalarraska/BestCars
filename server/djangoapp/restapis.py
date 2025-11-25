# Uncomment the imports below before you add the function code
import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url',
    default="http://localhost:3030"
)
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/"
)


def get_request_custom(endpoint, **kwargs):
    params = ""
    if kwargs:
        for key, value in kwargs.items():
            params = params + key + "=" + value + "&"

    request_url = backend_url + endpoint + "?" + params
    print(f"GET from {request_url} ")

    try:
        response = requests.get(request_url)
        json_data = response.json()

        if isinstance(json_data, str):
            raise Exception("Invalid response: " + json_data)

        return json_data

    except Exception:
        print("Network exception occurred")

        try:
            from django.conf import settings
            import json

            json_path = settings.BASE_DIR / 'database/data'

            # ----- FETCH DEALERS -----
            if "/fetchDealers" in endpoint:
                with open(json_path / 'dealerships.json', 'r') as f:
                    data = json.load(f)
                    dealers = data['dealerships']

                if ("/fetchDealers/" in endpoint and
                        endpoint != "/fetchDealers"):
                    state = endpoint.split("/fetchDealers/")[1]
                    return [
                        d for d in dealers if d['state'] == state
                    ]

                return dealers

            # ----- FETCH REVIEWS -----
            if "/fetchReviews" in endpoint:
                with open(json_path / 'reviews.json', 'r') as f:
                    data = json.load(f)
                    reviews = data['reviews']

                if "/dealer/" in endpoint:
                    dealer_id = int(
                        endpoint.split("/dealer/")[1]
                    )
                    return [
                        r for r in reviews
                        if r['dealership'] == dealer_id
                    ]

                return reviews

            # ----- FETCH SINGLE DEALER -----
            if "/fetchDealer/" in endpoint:
                with open(json_path / 'dealerships.json', 'r') as f:
                    data = json.load(f)
                    dealers = data['dealerships']

                dealer_id = int(
                    endpoint.split("/fetchDealer/")[1]
                )

                for d in dealers:
                    if d['id'] == dealer_id:
                        return d

        except Exception as e:
            print(f"Mock data error: {e}")

        return None
