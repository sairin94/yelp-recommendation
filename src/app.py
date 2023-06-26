from flask import Flask, render_template,request
from flask_cors import cross_origin
import pickle
import numpy as np
import requests
from urllib.parse import quote


app = Flask(__name__)

restaurant_aspect=pickle.load(open('./data/business_final_metric.pkl','rb'))

@app.route('/')
def index():
    return render_template('index.html',business_id = list(restaurant_aspect['business_id'].values), name = list(restaurant_aspect['name'].values))


@app.route('/restaurant_details', methods=['POST'])
@cross_origin(origins=['http://localhost:5000', 'http://127.0.0.1:5000'])
def display_details_aspect():
    business_id = request.form.get('myselect')

    API_KEY = 'AIzaSyB2NzwqnLD20WafDa4nEBe4-SnZHjxETbU'
    print("business_id = {}".format(business_id))
    index = np.where(restaurant_aspect.business_id==business_id)[0][0]
    target_row = restaurant_aspect.iloc[index]
    print("index = {}".format(index))
    name=target_row['name']
    stars=np.round(target_row['stars'],2)
    address=target_row['address']
    city=target_row['city']
    state=target_row['state']
    full_address=quote(address + ', ' + city + ', ' + state)
    sentiment_score=target_row['sentiment_score']
    food_quality=target_row['food_quality']
    price=target_row['price']
    ambiance=target_row['ambiance']
    service=target_row['service']
    comfort=target_row['comfort']


    return render_template('restaurant_details.html', 
                           name=name, 
                           stars=stars,
                           full_address=full_address,
                           sentiment_score=sentiment_score, 
                           food_quality=food_quality,
                           price=price,
                           ambiance=ambiance,
                           service=service,
                           comfort=comfort)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
