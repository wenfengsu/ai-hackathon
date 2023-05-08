import os

import openai
import pandas as pd
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_type = "azure"
openai.api_base = "https://hackathontest2.openai.azure.com/"
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
            reviews_text = str(headers["reviews.text"])
            name = str(headers["name"])
            if name != hotel:
                continue
            existing_review = reviews.get(name)
            if existing_review == None:
                reviews[name] = reviews_text    
            else: 
                reviews[name] = existing_review + reviews_text
            
        results = ""
        for key, value in reviews.items():
            reviews_text_string = value
            trimmed_reviews = reviews_text_string[0:4096]
            response = openai.Completion.create(
                engine="TextDavinci003Test1",
                prompt=generate_prompt(trimmed_reviews),
                temperature=0.3,
                max_tokens=250,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                best_of=1,
                stop=None)
            results = response.choices[0].text.strip()

        return redirect(url_for("index", result=results))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(review_content_string):
    return "Summarize the following review content in 50 words" + review_content_string + "\n\nSummary:"
