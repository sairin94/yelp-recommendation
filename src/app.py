from flask import Flask, render_template,request
from flask_cors import cross_origin
import pickle
import numpy as np
import requests
from urllib.parse import quote


app = Flask(__name__)

restaurant_philadelphia_df = pickle.load(open('/Users/sairindhri/yelp-data-analysis2/src/data/top_restaurant_philadelphia.pkl','rb'))
prediction_model = pickle.load(open('/Users/sairindhri/yelp-data-analysis2/src/data/svm_sentiment_prediction_model.pkl','rb'))



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/restaurant_details', methods=['POST'])
@cross_origin(origins=['http://localhost:5000', 'http://127.0.0.1:5000'])
def display_details():
    user_input = request.form.get('myselect')

    API_KEY = 'AIzaSyB2NzwqnLD20WafDa4nEBe4-SnZHjxETbU'
    address = '1600 Amphitheatre Parkway, Mountain View, CA' # replace with your address

    # Step 1: Get Place data from address
    response = requests.get(f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={address}&inputtype=textquery&fields=photos&key={API_KEY}")
    data = response.json()

    photoUrl = ""

    if 'candidates' in data and len(data['candidates']) > 0 and 'photos' in data['candidates'][0] and len(data['candidates'][0]['photos']) > 0:
        photoReference = data['candidates'][0]['photos'][0]['photo_reference']
        print("photoReference:", photoReference)
        # Step 2: Get Photo from Photo Reference
        photoUrl = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photoReference}&key={API_KEY}"
        # photoUrl.replace('&amp;', '&')
        print("photoUrl:", photoUrl)

    # selected_restaurant = request.form.get('myselect')
    # all_restaurants = request.form.get('allRestaurants').split(',')
    # continue with your logic here...
    print(str(user_input))
    return render_template('restaurant_details.html', photo_url=photoUrl)

if __name__ == '__main__':
    app.run(debug=True)