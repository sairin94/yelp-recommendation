from flask import Flask, render_template,request
from flask_cors import cross_origin
import pickle
import numpy as np
import requests
from urllib.parse import quote


app = Flask(__name__)

restaurant_sentiment_final = pickle.load(open('/Users/sairindhri/yelp-data-analysis2/src/data/restaurant_sentiment_final.pkl','rb'))

@app.route('/')
def index():
    return render_template('index.html',business_id = list(restaurant_sentiment_final['business_id'].values), name = list(restaurant_sentiment_final['name'].values))

@app.route('/restaurant_details', methods=['POST'])
@cross_origin(origins=['http://localhost:5000', 'http://127.0.0.1:5000'])
def display_details():
    business_id = request.form.get('myselect')

    API_KEY = 'AIzaSyB2NzwqnLD20WafDa4nEBe4-SnZHjxETbU'

    # selected_restaurant = request.form.get('myselect')
    # all_restaurants = request.form.get('allRestaurants').split(',')
    # continue with your logic here...
    print("business_id = {}".format(business_id))
    index = np.where(restaurant_sentiment_final.business_id==business_id)[0][0]
    target_row = restaurant_sentiment_final.iloc[index]
    print("index = {}".format(index))
    name=target_row['name']
    average_stars=np.round(target_row['average_star'],2)
    negative_reviews=target_row['negative_reviews']
    positive_reviews=target_row['positive_reviews']
    neutral_reviews=target_row['neutral_reviews']
    address=target_row['address']
    city=target_row['city']
    state=target_row['state']
    full_address=quote(address + ', ' + city + ', ' + state)


    return render_template('restaurant_details.html', 
                           name=name, 
                           average_stars=average_stars,
                           negative_reviews=negative_reviews,
                           neutral_reviews=neutral_reviews,
                           positive_reviews=positive_reviews,
                           full_address=full_address)

if __name__ == '__main__':
    app.run(debug=True)