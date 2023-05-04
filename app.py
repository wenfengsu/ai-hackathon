import os

import openai
import pandas as pd
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_type = "azure"
openai.api_base = "https://reviewscons.openai.azure.com/"
openai.api_version = "2022-12-01"
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        hotel = request.form["hotel"]
        
        df = pd.read_csv("./data/Datafiniti_Hotel_Reviews.csv")
        df_10 = df.head(10)

        reviews = {}
        for index, headers in df.iterrows():
            review_content = str(headers["reviews.text"])
            name = str(headers["name"])
            print(hotel, name)
            if name != hotel:
                continue
            existing_review = reviews.get(name)
            if existing_review == None:
                reviews[name] = review_content    
            else: 
                reviews[name] = existing_review + review_content
            
        results = ""
        for key, value in reviews.items():
            review_content_string = value
            response = openai.Completion.create(
                engine="ReviewSummary",
                prompt=generate_prompt(review_content_string),
                temperature=0.3,
                max_tokens=250,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                best_of=1,
                stop=None)
            results = response.choices[0].text.strip()
            # results[key] = generated_text
            print(key)
            print(results)
            print("\n\n")
        return redirect(url_for("index", result=results))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(review_content_string):
    return "Summarize the following review content in 100 words" + review_content_string + "\n\nSummary:"
