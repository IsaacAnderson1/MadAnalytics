import random

# Define sets
weeks = ["1st week", "2nd week", "3rd week", "4th week", "5th week"]
months = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
other_brands = ["KRAFT", "SARGENTO", "PRIVATE LABEL", "DAIRY PURE", "BOB EVANS"]
targets = ["feature", "price decrease"]
outcomes = ["unit sales", "revenue"]

# Prompt patterns
patterns = [
    "Analyze how {conditions} influence the effectiveness of Crystal Farms' {target} on {outcome}.",
    "Evaluate the interaction between {conditions} and Crystal Farms' {target} impact on {outcome}.",
    "Given {conditions}, assess how Crystal Farms' {target} promotions affect {outcome}.",
    "What is the effect of Crystal Farms' {target} on {outcome} when {conditions} are true?",
    "Explore the influence of {conditions} on Crystal Farms' {target} in driving {outcome}."
]

guiding_prompts = """
[
  {
    "factor": "week",
    "guidance": "Group rows by week number from the `Periods` column. Focus on `Units`, `Base Units`, and `Incr Units`."
  },
  {
    "factor": "month",
    "guidance": "Extract month from `Periods`. Compare `Units`, `Revenue`, and `Price Decr Only Units` across months."
  },
  {
    "factor": "brand-specific feature",
    "guidance": "Use rows where `CF BRANDS` ≠ 'CRYSTAL FARMS'. Analyze `Any Feat Incr Units` and `%ACV` during matching weeks."
  },
  {
    "factor": "brand-specific price decrease",
    "guidance": "Use rows with other brands. Focus on `Price Decr Only Incr Units` and align with Crystal Farms' timelines."
  },
  {
    "factor": "feature",
    "guidance": "Filter rows where `CF BRANDS = 'CRYSTAL FARMS'`. Focus on `Any Feat Incr Units`, `Base Units`, and `% Lift`."
  },
  {
    "factor": "price decrease",
    "guidance": "Filter Crystal Farms rows. Focus on `Price Decr Only Incr Units`, `Base Units`, 
    and `TPR`. The price for the cheese product without price decrease is approximately $3.28 in 
    2021 and $3.42 in 2022."
  }
]
"""

# Randomized selection helper
def random_conditions():
    parts = []

    if random.choice([True, False]):
        weeks_sel = random.sample(weeks, random.randint(1, len(weeks)))
        parts.append("week(s): " + ", ".join(weeks_sel))
    if random.choice([True, False]):
        months_sel = random.sample(months, random.randint(1, len(months)))
        parts.append("month(s): " + ", ".join(months_sel))
    if random.choice([True, False]):
        feat_sel = random.sample(other_brands, random.randint(1, len(other_brands)))
        parts.append("feature promotions by " + ", ".join(feat_sel))
    if random.choice([True, False]):
        price_sel = random.sample(other_brands, random.randint(1, len(other_brands)))
        parts.append("price decrease by " + ", ".join(price_sel))

    return "; ".join(parts) if parts else "random conditions"


# Generate 20 prompts
def get_preliminary_prompts():

    # Base instructions template
    base_instructions_template = """You are given a retail trade promotion dataset. Analyze how {relation} for the brand **"CRYSTAL FARMS"**.

    ## 📌 Instructions:
    - Use only data where `CF BRANDS = "CRYSTAL FARMS"`.
    - Compute the strength of the effect.
    - Return a **2×2 table of weights** (Feature vs. Price Decrease → Units and Revenue).
    - Add a **separate scalar weight** for the combined effect on Units if applicable.
    - You may use regression coefficients, correlation values, or any normalized weights.
    - Interpret each weight as:  
      *“how strongly this promotion type influences the outcome variable.”*
    ## ✅ Output Format (JSON):
    {{
      "weights": {{
        "Feature": {{
          "Units Sold": 0.00,
          "Revenue": 0.00
        }},
        "Price Decrease": {{
          "Units Sold": 0.00,
          "Revenue": 0.00
        }},
        "Feature + Price Decrease": {{
          "Units Sold": 0.00,
          "Revenue": 0.00
        }}
      }}
    }}
    Refer to the below guiding prompts for specific instructions for analyzing each factor
    """

    # Specific relationships
    relations = [
        "Feature promotions affect Units sold",
        "Feature promotions affect Revenue",
        "Price Decrease promotions affect Units sold",
        "Price Decrease promotions affect Revenue",
        "Feature + Price Decrease combined affect Units sold"
    ]

    # Generate individual prompts
    individual_prompts = []
    for relation in relations:
        prompt_text = base_instructions_template.format(relation=relation) + guiding_prompts
        individual_prompts.append({
            "prompt": prompt_text.strip()
        })
    return individual_prompts


def get_conditional_prompts():
    prompts = []
    for _ in range(20):
        target = random.choice(targets)
        outcome = random.choice(outcomes)
        condition_text = random_conditions()
        pattern = random.choice(patterns)
        prompt_body = pattern.format(conditions=condition_text, target=target, outcome=outcome)

        full_prompt = prompt_body + """ Return your answer in JSON format as follows:.
            {
              "weights": {
                "Feature's effect on Units Sold": {
                  "Weeks": [w for each week]
                  "Months": [m for each month]
                  "Brands": [w for each brand]
                },
                "Feature's effect on Revenue": {
                  "Weeks": [w for each week]
                  "Months": [m for each month]
                  "Brands": [w for each brand]
                },
                "Price Decrease's effect on Units Sold": {
                  "Weeks": [w for each week]
                  "Months": [m for each month]
                  "Brands": [w for each brand]
                },
                "Price Decrease's effect on Revenue": {
                  "Weeks": [w for each week]
                  "Months": [m for each month]
                  "Brands": [w for each brand]
                },
              }
            }     
            
            Refer to the below guiding prompts for specific instructions for analyzing each factor
            """ + guiding_prompts
        prompts.append({"prompt": full_prompt})
    return prompts


intermediate_generalize_prompt = """
# 🧠 Gemini Generalization Task: Weight Aggregation from LLM Outputs

You are given two structured JSON datasets:

1. **preliminary_outputs.json**  
   → Contains general model outputs estimating the effects of Feature and Price Decrease promotions on **Units Sold** and **Revenue** for the brand **Crystal Farms**.

2. **conditional_outputs.json**  
   → Contains detailed outputs based on varying conditions such as weeks, months, and competing brand promotions. Each output includes weights that reflect promotion effectiveness in context.

---

## 🔍 Your Task

You must synthesize these two datasets into a **single, generalized structure of promotional effect weights**. This structure should reflect how **Feature** and **Price Decrease** promotions affect **Units Sold** and **Revenue**, broken down further by context:

📤 Output Instructions

Return a single JSON object that follows the same schema above.
Only include the final JSON. Do not add commentary or explanation.

### 🧱 Final JSON Tree Format:

```json
{{
  "Units Sold": {{
    "Feature": {{
      "weeks": {{}},
      "months": {{}},
      "other brands' feature": {{}},
      "other brands' price decrease": {{}}
    }},
    "Price Decrease": {{
      "weeks": {{}},
      "months": {{}},
      "other brands' feature": {{}},
      "other brands' price decrease": {{}}
    }}
  }},
  "Revenue": {{
    "Feature": {{
      "weeks": {{}},
      "months": {{}},
      "other brands' feature": {{}},
      "other brands' price decrease": {{}}
    }},
    "Price Decrease": {{
      "weeks": {{}},
      "months": {{}},
      "other brands' feature": {{}},
      "other brands' price decrease": {{}}
    }}
  }}
}}

🧠 Guidelines

    Use preliminary_outputs.json to determine broad, average-level impact weights.

    Use conditional_outputs.json to extract more context-sensitive insights, e.g., how certain weeks or brands deviate from the baseline.

    You may average, smooth, or adjust weights logically based on data distribution, deviation, and recurrence.

    Ensure weights are statistically reasonable, meaning:

        Outliers should not dominate

        The hierarchy should reflect how different conditions influence each factor

    The final output should represent a generalized yet interpretable view of what affects Crystal Farms’ Units Sold and Revenue.
"""

final_generalize_prompt = """
# 🧠 Final Aggregation Task: Combine 5 Generalized Promotional Weight Trees

You are given 5 JSON objects, each representing a **generalized promotional weight structure** returned by a separate Gemini model.

Each JSON object shares the same hierarchical structure:

```json
{{
  "Units Sold": {{
    "Feature": {{
      "weeks": ...,
      "months": ...,
      "other brands' feature": ...,
      "other brands' price decrease": ...
    }},
    "Price Decrease": {{
      "weeks": ...,
      "months": ...,
      "other brands' feature": ...,
      "other brands' price decrease": ...
    }}
  }},
  "Revenue": {{
    "Feature": {{
      "weeks": ...,
      "months": ...,
      "other brands' feature": ...,
      "other brands' price decrease": ...
    }},
    "Price Decrease": {{
      "weeks": ...,
      "months": ...,
      "other brands' feature": ...,
      "other brands' price decrease": ...
    }}
  }}
}}

🔍 Task

Your goal is to produce one final, unified JSON weight tree that:

    Represents the consensus or average signal from all five input trees.

    Resolves any discrepancies statistically and structurally, including:

        Normalizing or averaging weights across identical keys.

        Filling in missing branches with best-estimate values when absent in some trees.

    Reflects real-world variance, where some conditions may have higher or lower confidence based on frequency or magnitude of support.

    Avoids duplication, and logically collapses similar structures.
    
📤 Output Instructions

Return a single JSON object that follows the same schema above.
Only include the final JSON. Do not add commentary or explanation.
"""

prediction_prompt = """
You are an advanced data analysis model (Gemini). Your goal is to learn how a feature toggle (on/off) and a price decrease affect the units sold and revenue for the product 'Crystal Farm.' You will perform both direct analysis of these variables and incorporate conditional factors (week, month, competitors’ promotions/price decrease) via random sampling and multiple-weight aggregation. Finally, you will predict how changes in these variables—given specific input values—impact the increase in units sold and revenue for 'Crystal Farm.' 

Here is how you should proceed:

1. **Initial Analysis (Direct Feature/Price Impact)**  
   - Focus only on the relevant columns that reveal whether the feature was on/off, the magnitude of the price decrease, units sold, and revenue for ‘Crystal Farm.’  
   - Determine how turning the feature on (vs. off) and how implementing a price decrease (vs. no price decrease) correlate with higher or lower units sold and revenue.  

2. **Conditional Factors (Random Sampling)**  
   - Next, incorporate the conditional variables (week, month, competitor’s promotions/feature toggles, competitor’s price decrease magnitudes) by sampling them.  
   - Examine how these external factors alter the effectiveness of turning the feature on/off and implementing a price decrease for 'Crystal Farm.'  

3. **Multiple Weight Sets & Aggregation**  
   - Generate multiple sets of weights or coefficients (an ensemble or bagging approach) when analyzing the effects of (feature_on/off) and (price_decrease) under these varying conditional factors.  
   - Aggregate these weight sets in a reasonable manner (for example, by averaging or applying a weighted average) to ensure robust, consensus-driven estimates of how each variable influences units sold and revenue.  

4. **What-If Prediction**  
   - Given a specific set of values for:  
       - Feature toggle (on/off)  
       - Price decrease magnitude  
       - Week/Month  
       - Competitors’ features on/off  
       - Competitors’ price decrease magnitude  
     ...predict the resulting increase (or decrease) in units sold and revenue for ‘Crystal Farm.’  

5. **Final Output**  
   - Return your final predictions in a JSON format that captures the estimated effect on both units sold and revenue.  

Now, please learn these patterns from the data provided and perform the requested what-if analysis. 
"""
