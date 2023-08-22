from flask import Flask, render_template, request, jsonify
from flask_cors import cross_origin
import pickle
import numpy as np
import pandas as pd
from urllib.parse import quote
import json
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import random

app = Flask(__name__)

philadelphia_restaurants_cuisine_details=pickle.load(open('./src/data/restaurant_philadelphia_details_cuisine.pkl','rb'))
with open('./src/data/5_restaurants_aggregated.pkl', 'rb') as f:
    restaurant_five_philadelphia = pickle.load(f)

class Restaurant:
    def __init__(self, name, id, latitude, longitude) -> None:
        self.name = name
        self.id=id
        self.latitude = latitude
        self.longitude = longitude


def processABSAData(data_dict):
    organized_data = {
        'name': 'Reviews',
        'children': []
    }
    
    # Mapping for the top-level categories
    category_mapping = {
        'ambience': 'Ambience',
        'restaurant': 'Restaurant',
        'food': 'Food',
        'drinks': 'Drinks',
        'location': 'Location',
        'service': 'Service'
    }

    # Categories without children
    no_children_categories = ['ambience', 'service', 'location']

    for key, value in data_dict.items():
        category, sub_category = key.split(' ')

        top_level = next((item for item in organized_data['children'] if item['name'] == category_mapping[category]), None)

        if not top_level:
            if category in no_children_categories:
                top_level = {
                    'name': category_mapping[category],
                    'Positive': value[0],
                    'Negative': value[1],
                    'Neutral': value[2]
                }
            else:
                top_level = {'name': category_mapping[category], 'children': []}
            organized_data['children'].append(top_level)

        if category not in no_children_categories:
            # if sub_category == 'general':
            #     sub_category = 'name'  # Replacing "general" with "name"

            top_level['children'].append({
                'name': sub_category,
                'Positive': value[0],
                'Negative': value[1],
                'Neutral': value[2]
            })

    return organized_data

def generate_wordcloud(data_dict):
    # Calculate total count for each aspect
    total_counts = {aspect: sum(counts) for aspect, counts in data_dict.items()}
    
    # Calculate color scale values for each aspect
    colormap = matplotlib.cm.RdYlGn
    colormap_values = {
        aspect: matplotlib.colors.rgb2hex(
            colormap(
                ((counts[0] - counts[1]) / total_counts[aspect] + 1) / 2
            )[:3]
        )
        for aspect, counts in data_dict.items()
    }

    def color_func(word, **kwargs):
        return colormap_values[word]

    wordcloud = WordCloud(
        width=1200, height=800, background_color="white", color_func=color_func
    ).generate_from_frequencies(total_counts)

    # Plotting
    fig = plt.figure(figsize=(16, 10.666667))
    ax = fig.add_axes([0.05, 0.05, 0.8, 0.9])  # adjust these values as needed
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')

    # Create a new axis for the colorbar beside the word cloud
    cax = fig.add_axes([0.87, 0.2, 0.02, 0.6])
    cb = matplotlib.colorbar.ColorbarBase(cax, cmap=colormap, orientation='vertical', norm=matplotlib.colors.Normalize(vmin=-1, vmax=1))
    cb.set_label('Sentiment')

    # Save the image to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    # Encode the image to base64
    encoded_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    plt.close(fig)  # Close the figure to free up memory

    return encoded_image


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getRestaurants', methods=['POST'])
@cross_origin(origins=['http://localhost:8080', 'http://127.0.0.1:8080'])
def get_restaurants():
    # Boundary received from the frontend
    boundary = request.get_json()['boundary']
    cuisine= request.get_json()['cuisine']
    print('boundary',boundary)
    
    lat_min = boundary["south"]
    lat_max = boundary["north"]
    long_min = boundary["west"]
    long_max = boundary["east"]
    #restaurant matching specific cuisine type
    filtered_cuisine=philadelphia_restaurants_cuisine_details.loc[philadelphia_restaurants_cuisine_details['closest_cuisine']==cuisine]

     # Filter the DataFrame based on latitude and longitude boundaries
    restaurants_within_boundary = filtered_cuisine.loc[
    (filtered_cuisine["latitude"] >= lat_min) &
    (filtered_cuisine["latitude"] <= lat_max) &
    (filtered_cuisine["longitude"] >= long_min) &
    (filtered_cuisine["longitude"] <= long_max)
]
    
    # Sort the filtered DataFrame by review_count in descending order
    top_ten_restaurant = restaurants_within_boundary.sort_values(by="review_count", ascending=False)[:15]

    # print('top 15 restaurant',top_ten_restaurant)
    top_ten_restaurant_instances = [
        Restaurant(name=row["name"],id=row["business_id"],latitude=row["latitude"], longitude=row["longitude"])
        for _, row in top_ten_restaurant.iterrows()
    ]

    # Convert the list of Restaurant instances into a JSON serializable format
    top_ten_restaurant_json = [{'name': r.name,'id':r.id, 'position': {'lat': r.latitude, 'lng': r.longitude}} for r in top_ten_restaurant_instances]


    return jsonify(top_ten_restaurant_json)

@app.route('/restaurant_detail',methods=['POST'])
@cross_origin(origins=['http://localhost:5000', 'http://127.0.0.1:5000'])
def display_restaurant_aspect():
    details_row = restaurant_five_philadelphia.iloc[random.randint(0, 4)]
    # get star ratings, defaulting to 0 if a rating doesn't exist
    star_counts = {
        1: details_row['stars'].get(1.0, 0),
        2: details_row['stars'].get(2.0, 0),
        3: details_row['stars'].get(3.0, 0),
        4: details_row['stars'].get(4.0, 0),
        5: details_row['stars'].get(5.0, 0),
    }
    total_num_reviews = sum([star_counts[i] for i in range(1,6)])
    name=request.form.get('restaurant_name')
    stars=np.round(details_row['avg_stars'],1)
    address=details_row['address']
    city=details_row['city']
    state=details_row['state']
    full_address=quote(address + ', ' + city + ', ' + state)
    absa_data = processABSAData(details_row['sentiment_dict'])
    wordcloud_image  = generate_wordcloud(details_row['aspect_dict'])

    return render_template('restaurant_details.html',name=name, 
                                                    full_address=full_address, 
                                                    star_counts=star_counts, 
                                                    stars=stars, 
                                                    total_num_reviews=total_num_reviews,
                                                    absa_data=absa_data,
                                                    wordcloud_image=wordcloud_image)

def generate_wordcloud_base64(df):
    # Convert the dataframe into dictionary {word: frequency}
    freq = df.set_index('Aspect')['Total Count'].to_dict()

    # Get the colormap
    colormap = matplotlib.colormaps['RdYlGn']

    # Calculate the color scale value
    df['Colormap Value'] = df.apply(lambda row: matplotlib.colors.rgb2hex(colormap(((row['Positive Count'] - row['Negative Count']) / row['Total Count'] + 1) / 2)[:3]), axis=1)

    def color_func(word, **kwargs):
        return df[df['Aspect'] == word]['Colormap Value'].values[0]

    wordcloud = WordCloud(width=1200, height=800, background_color="white", color_func=color_func).generate_from_frequencies(freq)

    # Plotting
    fig, ax = plt.subplots(figsize=(16, 10.666667))
    # Display the word cloud
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')

    # Create a new axis for the colorbar beside the word cloud
    cax = fig.add_axes([0.93, 0.2, 0.02, 0.6])
    # Display the colorbar
    cb = matplotlib.colorbar.ColorbarBase(cax, cmap=colormap, orientation='vertical', norm=matplotlib.colors.Normalize(vmin=-1, vmax=1))
    cb.set_label('Sentiment')

    # Save the image to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    # Encode the image to base64
    encoded_image = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    plt.close(fig)  # Close the figure to free up memory

    return encoded_image


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
