import requests
import json
import string
from sklearn.metrics import precision_recall_fscore_support

from config import (authoringKey, app_id, authoringEndpoint, slot_name)

#from program.config import (AUTHORING_KEY, APP_ID, APP_VERSION_ID, PREDICTION_ENDPOINT, SLOT_NAME)

connexion_string = f"{authoringEndpoint}luis/prediction/v3.0/apps/{app_id}/slots/{slot_name}/predict"
headers = {}

class performance_evaluator():
    """
    Evaluate Luis model performances for both intents and entities predictions.
    """


    def __init__(self, ground_truth, entities_name):
        """
        Input :
            ground_truth (dict) : dictionnary built from a json file that contains utterances and their related intents and entities
            entities_name (list of str) : list of the names of the entities
        """
        self.ground_truth = ground_truth
        self.entities_name = entities_name


    def get_prediction(self, text):
        """
        Send a request to the Luis model to get the predictions of a given utterance
        Input :
            text (str) : utterance to predict
        Output :
            response.json() : json file containing the predictions
        """

        params = {
        'query': text,
        'timezoneOffset': '0',
        'verbose': 'true',
        'show-all-intents': 'true',
        'spellCheck': 'true',
        'staging': 'false',
        'subscription-key': authoringKey
        }
        response = requests.get(connexion_string, headers=headers, params=params)
        return response.json()


    def get_ground_truth_entity(self, entities, entity_name):
        """
        Remove punctuation from ground truth entities so that we can compare it to prediction
        Input :
            entities (list of dict) : list of entities labeled in a single turn. Ex of format :
                [{'entity': 'To',
                    'startPos': 59,
                    'endPos': 65,
                    'children': [{'entity': 'Airport', 'startPos': 59, 'endPos': 65}]},
                {'entity': 'From',
                    'startPos': 37,
                    'endPos': 55,
                    'children': [{'entity': 'Airport', 'startPos': 37, 'endPos': 55}]},
                {'entity': 'Departure_date', 'startPos': 104, 'endPos': 113}]
            entity_name (str) : ex: 'To'
        Output :
            entity (str) : value of entity without punctuation (ex : october 16th)
        """
        
        try:
            entity = entities[entity_name][0]["text"]
            entity = entity.translate(str.maketrans("", "", string.punctuation)) # remove punctuation
            return entity
        except KeyError:
            return ""


    def evaluate_intents_performance(self):
        """
        Calculate intents prediction performance
        Output :
            precision (float)
            recall (float)
            f_score (float)
        """
        # Get true intents
        intents_true = []
        intents_pred = []

        # Calculate predicted intents
        for turn in self.ground_truth:
            #print("line 90", turn["text"])
            text = turn["text"]
            params = {
            'query': text,
            'timezoneOffset': '0',
            'verbose': 'true',
            'show-all-intents': 'true',
            'spellCheck': 'false',
            'staging': 'false',
            'subscription-key': authoringKey
            }
            response = requests.get(connexion_string, headers=headers, params=params)
            response = response.json()
            #print("line 100", response)
            try: # there may be some instances where responce["predicion"] doesn't exist
                intent_pred = response["prediction"]["topIntent"]
                intents_pred.append(intent_pred)
                # Keep intent_true evalauted after intent_pred to make sure that the 2 tables have the same length 
                intent_true = turn["intent"]
                intents_true.append(intent_true)
            except KeyError:
                pass
        #print("line 110", intents_pred)
        #print("line 110", intents_true)

        precision, recall, fscore, _ = precision_recall_fscore_support(intents_true, intents_pred, average="micro")

        return precision, recall, fscore


    def build_dictionnaries(self, turn):
        """
        build groud truth and prediction dictionnaries for a single turn
        Input :
            turn (dict) : dictionnary of labeled intent and entities. Ex of format :
                {'text': 'Good day, please book me a trip from Vancouver, Jamaica to Recife. I would like to leave for 17 days on August 24.',
                    'intent': 'BookFlight',
                    'entities': [{'entity': 'To',
                        'startPos': 59,
                        'endPos': 65,
                        'children': [{'entity': 'Airport', 'startPos': 59, 'endPos': 65}]},
                            {'entity': 'From',
                            'startPos': 37,
                            'endPos': 55,
                        'children': [{'entity': 'Airport', 'startPos': 37, 'endPos': 55}]},
                            {'entity': 'Departure_date', 'startPos': 104, 'endPos': 113}]}
        Output :
            groud_truth_dict (dict) : dictionnary of ground truth entities. Ex of format :
                {'From': 'Vancouver',
                 'To': 'Recife',
                 'Departure_date': 'August 24',
                 'Return_date': '',
                 'budget': ''}
            predcition_dict (dict) : dictionnary of predicted entities. Same format as groud_truth_dict.
        """

        ground_truth_dict = {}
        prediction_dict = {}
        
        
        # Initialize dictionnaries at each turn
        for entity in self.entities_name:
            ground_truth_dict[entity] = ""
            prediction_dict[entity] = ""

        print("---157---")
        print(ground_truth_dict)
        print(prediction_dict)

        # Get prediction
        text = turn["text"]
        prediction = self.get_prediction(text)
        print("---164---")
        print('prediction', prediction)

        # Build prediction dictionnary

        for i in turn["entities"]:
            entity_name = i["entity"]
            start = i["startPos"]
            end = i["endPos"]
            entity_value = turn["text"][start: end]
            entity_value = entity_value.translate(str.maketrans("", "", string.punctuation))
            ground_truth_dict[entity_name] = entity_value

        # Build prediction dictionnary

        try: # if there is no entity found, "$instance" key doesn't exist
            entities = prediction["prediction"]["entities"]["$instance"]
            print("---181---")
            print(entities)
            prediction_dict["From"] = self.get_ground_truth_entity(entities, "From")
            prediction_dict["To"] = self.get_ground_truth_entity(entities, "To")
            prediction_dict["Departure_date"] = self.get_ground_truth_entity(entities, "Departure_date")
            prediction_dict["Return_date"] = self.get_ground_truth_entity(entities, "Return_date")
            prediction_dict["budget"] = self.get_ground_truth_entity(entities, "budget")
        except KeyError:
            pass

        return ground_truth_dict, prediction_dict


    def evaluate_entities_performance(self):
        """
        build y_true and y_pred lists for each entity so that we can calculate precision and recall
        Output :
            y_true_dict (dict) : dictionnary of true label for each entity
                (ex : {"From" : [ 0, 1, 1, 0], "To" : [...]...})
            y_pred_dict (dict) : dictionnary of predicted label for each entity. Same format as y_true
            correct_preds (list of bool) : number of correct predictions
        """
        y_true_dict = {}
        y_pred_dict = {}
        for entity in self.entities_name:
                #print("---199---\nTEST PERF ENTITIES")
                #print(entity)
                y_true_dict[entity] = []
                y_pred_dict[entity] = []
        correct_preds = []

        for turn in self.ground_truth:
            print("---206---\nTEST PERF ENTITIES")
            #print(self.ground_truth)
            print(turn)
            ground_truth_dict, prediction_dict = self.build_dictionnaries(turn)
            print(ground_truth_dict)
            print(prediction_dict)

            for entity in y_true_dict:
                try:
                    y_true = ground_truth_dict[entity]
                except KeyError:
                    y_true = ""
                try:
                    y_pred = prediction_dict[entity]
                except KeyError:
                    y_pred = ""

                if y_true == y_pred:
                    if y_true != "":
                        y_true_class = 1
                        y_pred_class = 1
                    else:
                        y_true_class = 0
                        y_pred_class = 0
                else:
                    if y_true != "":
                        y_true_class = 1
                        y_pred_class = 0
                    else:
                        y_true_class = 0
                        y_pred_class = 1

                y_true_dict[entity].append(y_true_class)
                y_pred_dict[entity].append(y_pred_class)
            
            correct_preds.append(ground_truth_dict == prediction_dict)
            
            
        return y_true_dict, y_pred_dict, correct_preds

 
def main():
    # Load data for evaluation
    # evaluation_file_name = "./data/evaluation_data.json"
    evaluation_file_name = "./data/evaluation_data_2.json"
    with open(evaluation_file_name, "r") as f:
        ground_truth = json.load(f)

    entities_name = ["From", "To", "Departure_date", "Return_date", "budget"]

    perf_ev = performance_evaluator(ground_truth, entities_name)

    print("\n----------- performances evaluation -------------")
    print("Sample size : ", len(ground_truth))

    # Evaluate intents prediction performance
    precision, recall, fscore = perf_ev.evaluate_intents_performance()
    print("\nIntents performances")
    print("\tPrecision = {:.2f}".format(precision))
    print("\tRecall = {:.2f}".format(recall))
    print("\tF-score = {:.2f}".format(fscore))

    # Evaluate entities prediction performance 
    print("\nEntities performance")
    y_true_dict, y_pred_dict, correct_preds = perf_ev.evaluate_entities_performance()
    #print("line 260", y_true_dict)
    #print("line 260", y_pred_dict)
    #print("line 260", correct_preds)

    for entity in y_true_dict:
        print("line 269", y_true_dict[entity])
        print("line 269", y_pred_dict[entity])
        print(precision_recall_fscore_support(y_true_dict[entity], y_pred_dict[entity], average="binary"))

        precision, recall, fscore, _ = precision_recall_fscore_support(y_true_dict[entity],
                                                                    y_pred_dict[entity],
                                                                    average="binary")
        print(f"\nentity '{entity}'")
        print("\tprecision = {:.2f}".format(precision))
        print("\trecall = {:.2f}".format(recall))
        print("\tF-score= {:.2f}".format(fscore))

    # Evaluate accuracy
    correct_preds_count = 0
    for i in correct_preds:
        correct_preds_count += correct_preds[i]
    accuracy = correct_preds_count / len(correct_preds)
    print("\nAccuracy = {:.0%}".format(accuracy))


    print(perf_ev.get_prediction("Hi im looking for a nice destination that i could go to from Columbus"))

if __name__ == "__main__":
    main()