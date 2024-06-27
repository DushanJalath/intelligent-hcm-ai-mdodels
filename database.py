from pymongo import MongoClient
from gridfs import GridFS

client = MongoClient('mongodb+srv://oshen:oshen@cluster0.h2my8yk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

database = client.HCM

collection_user = database["user"] 
collection_leave_predictions = database["LeavePredictions"]
collection_leave_predictions_dataset = database["Leave_prediction_dataset"]