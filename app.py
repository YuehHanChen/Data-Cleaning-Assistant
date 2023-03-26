import os
import pandas as pd
import re
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify
import openai

# Create necessary directories if they do not exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        file = request.files['datafile']
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Set the API key from the user input
        api_key = request.form['apikey']
        openai.api_key = api_key

        # Read the uploaded file
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))


        def generate_chat_response(prompt, model="gpt-3.5-turbo", tokens=800):
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=tokens,
                n=1,
                temperature=0.5,
            )

            return response['choices'][0]['message']['content']


        user_prompt = f"Imagine you are a data science consultant who only speaks English. Given the following dataset, please identify all the necessary data cleaning tasks before feeding the dataset to a machine learning model and \
            - all the possible cleaning tasks include: \
            1. Fill in missing values - if nan is more than 20%, than drop the columns \
                - fill mean/median or\
                - drop the columns\
            2. Handle outliers\
                - Remove outliers ⇒ remove data more than 3 std\
            3. Transform skewed data\
            4. Handle imbalanced data ⇒ Oversampling or undersampling\
            5. encoding(determine it's ordinal or categorical，encoding methods are different)\
            6. scale/normalize non-categorical data\
            follow the following instructions:\
            1. Write an outline of all the cleaning tasks you identified for this dataset\
            2. Generate Python/pandas code for each task. \
            Here is the dataset: {df.sample(20,replace=True)}\
            PLEASE BE AS CONCISE AS POSSIBLE"

        response_text = generate_chat_response(user_prompt)
        print(f"Generated response: {response_text}")
        
        # Return the response code to the frontend
        return jsonify(response =response_text)

    # Render the homepage
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
