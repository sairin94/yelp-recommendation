import requests
import json

class ASQPGenerator:
    def __init__(self, url):
        self.url = url
        self.system_prompt = "You are an NLP specialist, an expert in Aspect Based Sentiment Analysis of Yelp reviews.\n## Predict [(`aspect term`, `aspect category`, `sentiment polarity`, `opinion term`)...]\nText:"
        self.first_prompt = True
        self.grammar = r"""space ::= " "?
item-category ::= "`ambience general`" | "`drinks prices`" | "`drinks quality`" | "`drinks style_options`" | "`food prices`" | "`food quality`" | "`food style_options`" | "`location general`" | "`restaurant general`" | "`restaurant miscellaneous`" | "`restaurant prices`" | "`service general`"
sentiment ::= "`positive`" | "`negative`" | "`neutral`"
string ::=  "`" (
        [^"\\] |
        "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F])
      )* "`" space 
item ::= "(" space string "," space item-category "," space sentiment "," space string ")" space
root ::= "[" space (item ("," space item)*)? "]" space"""

    def add_sentence(self, user_prompt):
        if self.first_prompt:
            self.full_prompt = self.system_prompt
            self.first_prompt = False
        self.full_prompt += f"\nText:`{user_prompt}`"

    def add_labels(self, assistant_prompt):
        self.full_prompt += f"\nPrediction:{assistant_prompt}"
        
    def get_sentiment(self, review, n_predict=1024, temp=0.1, top_k=10, top_p=1.0):
        self.first_prompt = True
        self.add_sentence("The burger I ordered was great, but the ambience was too dark.")
        self.add_labels("[(`Burger`, `food quality`, `positive`, `great`), (`ambience`, `ambience general`, `negative`, `too dark`)]")
        self.add_sentence(review)
        result = self.parse_string(self.get_completion(n_predict, grammar="", temp=temp, top_k=top_k, top_p=top_p))
        return result
    
    def parse_string(self, input_str):
        # Escape single and double quotes
        escaped_str = input_str.replace("'", r"\'").replace('"', r'\"')

        # Convert backticks to single quotes
        final_str = escaped_str.replace('`', "'")

        try:
            parsed_list = eval(final_str)
            if not isinstance(parsed_list, list):
                raise ValueError("Input is not a list")

            for item in parsed_list:
                if not (
                    isinstance(item, tuple)
                    and len(item) == 4
                    and all(isinstance(element, str) for element in item)
                ):
                    raise ValueError("Tuple structure is incorrect")

            return parsed_list
        except (SyntaxError, ValueError) as e:
            print("Response: " + input_str)
            raise ValueError("Invalid input format") from e

    def get_completion(self, n_predict=1024, grammar="", temp=0.7, top_k=10, top_p=0.95):
        self.full_prompt += f"\nPrediction:"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "prompt": self.full_prompt,
            "n_predict": n_predict,
            "grammar": grammar,
            "temp": temp,
            "top_k": top_k,
            "top_p": top_p,
            "repeat_penalty": 1.1,
            "stop": ["]"]
        }
        response = requests.post(self.url, headers=headers, data=json.dumps(data))
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("content", None) + "]"
        else:
            raise ValueError(f"Error {response.status_code}: {response.text}")