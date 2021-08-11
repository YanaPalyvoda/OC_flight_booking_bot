# Microsoft Azure Language Understanding (LUIS) - Build App
#
# This script builds a LUIS app, entities, and intents using the Python
# LUIS SDK.  A separate sample trains and publishes the app.
#
# This script requires the Cognitive Services LUIS Python module:
#     python -m pip install azure-cognitiveservices-language-luis
#
# This script runs under Python 3.4 or later.

# Please Note that  the file booking_train_set.json mus be create before!

# <Dependencies>
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from msrest.authentication import CognitiveServicesCredentials

import datetime, json, os, time
# </Dependencies>

# <AuthorizationVariables>
authoring_key = '74485270f887423aa297c00418cf0f57'#'PASTE_YOUR_LUIS_AUTHORING_SUBSCRIPTION_KEY_HERE'

authoring_endpoint = 'https://p10luisbot-authoring.cognitiveservices.azure.com/'#'PASTE_YOUR_LUIS_AUTHORING_ENDPOINT_HERE'
# </AuthorizationVariables>

# <Client>
# Instantiate a LUIS client
client = LUISAuthoringClient(authoring_endpoint, CognitiveServicesCredentials(authoring_key))
# </Client>

train_utterances_path = "booking_train_set.json"

# <createApp>
def create_app():
    # Create a new LUIS app
    app_name    = "FlyMEbot" #FlyMEbot {}".format(datetime.datetime.now())
    app_desc    = "Flight booking app built with LUIS Python SDK."
    app_version = "0.2"
    app_locale  = "en-us"

    app_id = client.apps.add(dict(name=app_name,initial_version_id=app_version,
                                  description=app_desc,culture=app_locale))

    print("Created LUIS app {}\n    with ID {}".format(app_name, app_id))
    return app_id, app_version
# </createApp>

# Declare entities: 
# Creating an entity (or other LUIS object) returns its ID.
# We don't use IDs further in this script, so we don't keep the return value.
# <addEntities>
def add_entities(app_id, app_version):

    dstCityEntityId = client.model.add_entity(app_id, app_version, name="From")
    print("dstCityEntityId {} added.".format(dstCityEntityId))
    
    orCityEntityId = client.model.add_entity(app_id, app_version, name="To")
    print("orCityEntityId {} added.".format(orCityEntityId))
    
    strDateEntityId = client.model.add_entity(app_id, app_version, name="on_date")
    print("strDateEntityId {} added.".format(strDateEntityId))

    endDateEntityId = client.model.add_entity(app_id, app_version, name="end_date")
    print("endDateEntityId {} added.".format(endDateEntityId))  
    
    budgetEntityId = client.model.add_entity(app_id, app_version, name="budget")
    print("budgetEntityId {} added.".format(budgetEntityId))

# </addEntities>

# Declare an intent
# Creating an intent returns its ID, which we don't need, so don't keep.
# <addIntents>
def add_intents(app_id, app_version):
    intentId = client.model.add_intent(app_id, app_version, "BookFlight")

    print("Intent BookFlight {} added.".format(intentId))
# </addIntents>


# Helper function for creating the utterance data structure.
# <createUtterance>
def create_utterance(intent, utterance, *labels):
    """Add an example LUIS utterance from utterance text and a list of
       labels.  Each label is a 2-tuple containing a label name and the
       text within the utterance that represents that label.

       Utterances apply to a specific intent, which must be specified."""

    text = utterance.lower()

    def label(name, value):
        value = value.lower()
        start = text.index(value)
        return dict(entity_name=name, start_char_index=start,
                    end_char_index=start + len(value))

    return dict(text=text, intent_name=intent,
                entity_labels=[label(n, v) for (n, v) in labels])
# </createUtterance>

# Add example utterances for the intent.  Each utterance includes labels
# that identify the entities within each utterance by index.  LUIS learns
# how to find entities within user utterances from the provided examples.
#
# Example utterance: "find flights in economy to Madrid"
# Labels: Flight -> "economy to Madrid" (composite of Destination and Class)
#         Destination -> "Madrid"
#         Class -> "economy"
# <addUtterances>
def add_utterances(app_id, app_version):            

    with open("booking_train_set.json") as f:
        utterances = json.load(f)
    # Add the utterances in batch. You may add any number of example utterances
    # for any number of intents in one call.
    for i in range((len(utterances)//100)+1):
    #process_list(my_list[i*100:(1+i)*100])
        client.examples.batch(app_id, app_version, utterances[i*100:(1+i)*100])
        print(" {} examples utterance(s) added.".format(i))
# </addUtterances>

# <train>
def train_app(app_id, app_version):
    response = client.train.train_version(app_id, app_version)
    waiting = True
    while waiting:
        info = client.train.get_status(app_id, app_version)

        # get_status returns a list of training statuses, one for each model. Loop through them and make sure all are done.
        waiting = any(map(lambda x: 'Queued' == x.details.status or 'InProgress' == x.details.status, info))
        if waiting:
            print ("Waiting 10 seconds for training to complete...")
            time.sleep(10)
# </train>

# <publish>
def publish_app(app_id, app_version):
    responseEndpointInfo = client.apps.publish(app_id, app_version, is_staging=True)
    print("Application published. Endpoint URL: " + responseEndpointInfo.endpoint_url)
# </publish>

# <predict>
def predict(app_id, publishInfo, slot_name):

    request = { "query" : "Find flight to seattle" }

    # Note be sure to specify, using the slot_name parameter, whether your application is in staging or production.
    response = clientRuntime.prediction.get_slot_prediction(app_id=app_id, slot_name=slot_name, prediction_request=request)

    print("Top intent: {}".format(response.prediction.top_intent))
    print("Sentiment: {}".format (response.prediction.sentiment))
    print("Intents: ")

    for intent in response.prediction.intents:
        print("\t{}".format (json.dumps (intent)))
    print("Entities: {}".format (response.prediction.entities))
# </predict>

print("Creating application...")
app_id, app_version = create_app()
print()

print ("Adding entities to application...")
add_entities(app_id, app_version)
print ()

print ("Adding intents to application...")
add_intents(app_id, app_version)
print ()

print ("Adding utterances to application...")
add_utterances(app_id, app_version)
print ()

print ("Training application...")
train_app(app_id, app_version)
print ()

print ("Publishing application...")
publish_app(app_id, app_version)

## Clean up resources.
#print ("Deleting application...")
#client.apps.delete(app_id)
#print ("Application deleted.")
