import requests
import json
import os
from typing import List, Dict


class Rating:
    id: int
    score: int
    reasoning: str
    modelId: int
    userId: int
    modelName: str
    stlId: int
    binVoxId: int


# Replace A1 at the end with A<PAGE NUMBER> to get the next page of ratings
URL = "https://model-rating.vercel.app/api/trpc/rating.getRatingsWithPage?batch=1&input={%220%22%3A{%22json%22%3A{%22page%22%3A1}}}"


def getRatings() -> List[Rating]:
    response = requests.get(URL)
    data = json.loads(response.text)
    items = data[0]['result']['data']['json']

    return items
    
    
def main():
    ratings = getRatings()
    with open("data/ratings.json", "w") as f:
        f.write(json.dumps(ratings, indent=4))
        
        
if __name__ == "__main__":
    main()
    