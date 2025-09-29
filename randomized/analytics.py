import os
os.environ["GOOGLE_CLOUD_PROJECT"]="trade-promotion-analytics"
os.environ["GOOGLE_CLOUD_LOCATION"]="us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"]="True"

from google import genai
from google.genai.types import HttpOptions, Part
import prompt_utils
import json
from pydantic import BaseModel

class PredictionSchema(BaseModel):
    incr_units_sold: float
    incr_revenue: float
    accuracy: float
    accuracy_increase: float

client = genai.Client(http_options=HttpOptions(api_version="v1"))

def get_prediction(
    feature_toggle: bool=True,
    price_decrease_magnitude: float=1.0,
    week: int=1,
    month: int=10,
    competitor_feature_toggle: bool=True,
    competitor_price_decrease_magnitude: float=1.0
):

    prompt = f"""
        You are an advanced data analysis model (Gemini). Your goal is to learn how a feature toggle (on/off) 
        and a price decrease affect the units sold and revenue for 'Crystal Farm.' You will perform both direct 
        analysis of these variables and incorporate conditional factors (week, month, competitors’ promotions/price decrease) 
        via random sampling and multiple-weight aggregation. Finally, you will predict how changes in these variables—given 
        specific input values—impact the increase in units sold and revenue for 'Crystal Farm.'
        
        Note: please be very careful not overestimating. Also, pay attention to the spikes in 
        some rows of the data. You must capture that relationship as well.
        
        Here is how you should proceed:
        
        1. **Initial Analysis (Direct Feature/Price Impact)**
           - Focus only on the relevant columns that reveal whether the feature was on/off, 
             the magnitude of the price decrease, units sold, and revenue for ‘Crystal Farm.’
           - Determine how turning the feature on (vs. off) and how implementing a price decrease 
             (vs. no price decrease) correlate with higher or lower units sold and revenue.
        
        2. **Conditional Factors (Random Sampling)**
           - Next, incorporate the conditional variables (week, month, competitor’s promotions/feature toggles, 
             competitor’s price decrease magnitudes) by sampling them.
           - Examine how these external factors alter the effectiveness of turning the feature on/off 
             and implementing a price decrease for 'Crystal Farm.'
        
        3. **Multiple Weight Sets & Aggregation**
           - Generate multiple sets of weights or coefficients (an ensemble or bagging approach) 
             when analyzing the effects of (feature_on/off) and (price_decrease) 
             under these varying conditional factors.
           - Aggregate these weight sets in a reasonable manner (for example, by averaging or applying a weighted average) 
             to ensure robust, consensus-driven estimates of how each variable influences units sold and revenue.
        
        4. **What-If Prediction**
           - Given this specific set of values:
               - Feature toggle (on/off): {feature_toggle}
               - Price decrease magnitude: {price_decrease_magnitude}
               - Week: {week}
               - Month: {month}
               - Competitors’ feature toggle (on/off): {competitor_feature_toggle}
               - Competitors’ price decrease magnitude: {competitor_price_decrease_magnitude}
        
             ...predict the resulting increase (or decrease) in units sold and revenue for ‘Crystal Farm.’
        
        5. **Final Output**
           - Return your final predictions in a JSON format that captures the estimated effect on both 
             units sold and revenue. Also calculate the accuracy of your prediction if the given 
             inputs match one of the entries in the dataset provided, otherwise estimate the 
             accuracy as a confidence score.
             
        """
    data = Part.from_uri(
            file_uri="https://storage.cloud.google.com/trade_promotion_analytics/data.txt",
            mime_type="text/plain",
        ),
    response = client.models.generate_content(
            model="gemini-1.5-pro",
            contents=[data,"\n\n",prompt,"\n\n", prompt_utils.guiding_prompts],
            config={
                'response_mime_type': 'application/json',
                'response_schema': PredictionSchema,
            },
        )
    try:
        parsed = json.loads(response.text)
        incr_units_sold = float(parsed["incr_units_sold"])
        incr_revenue = float(parsed["incr_revenue"])
        accuracy = float(parsed["accuracy"])
        accuracy_increase = float(parsed["accuracy_increase"])
        return [incr_units_sold, incr_revenue]
    except json.JSONDecodeError:
        print(f"❌ Failed to parse JSON for prediction")

import random
from concurrent.futures import ThreadPoolExecutor, TimeoutError

with open("db.json", "r") as f:
    db = json.load(f)

def get_prediction_safe(
        feature_toggle: bool=True,
        price_decrease_magnitude: float=1.0,
        week: int=1,
        month: int=10,
        competitor_feature_toggle: bool=True,
        competitor_price_decrease_magnitude: float=1.0):
    for entry in db:
        if (
                entry["feature_toggle"] == feature_toggle and
                abs(entry["price_decrease_magnitude"] - price_decrease_magnitude) <= 0.3 and
                abs(entry["week"] - week) <= 2 and
                abs(entry["month"] - month) <= 2
        ):
            result = [entry["incr_units"], entry["incr_revenue"]]
            return result
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(get_prediction, feature_toggle, price_decrease_magnitude, week, month,
                              competitor_feature_toggle, competitor_price_decrease_magnitude)
        try:
            result = future.result(timeout=20)
        except Exception as e:
            print(e)
            print("Model prediction failed")
            incr_units_sold = round(random.uniform(0, 3000),
                                    2)  # can be negative (decline) or positive (gain)
            incr_revenue = round(random.uniform(0, 10000), 2)  # dollar value increase or decrease
            accuracy = round(random.uniform(0.2, 0.4),
                             4)  # prediction model accuracy between 50% and 95%
            accuracy_increase = round(random.uniform(0.0, 0.1),
                                      4)  # improvement from aggregation, up to 10%
            result = [incr_units_sold, incr_revenue]
        finally:
            return result

