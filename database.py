from pymongo import MongoClient
from gridfs import GridFS

client = MongoClient('mongodb://localhost:27017')

database = client.HCM

collection_user = database["user"] 
collection_leave_predictions = database["LeavePredictions"]
collection_leave_predictions_dataset = database["Leave_prediction_dataset"]