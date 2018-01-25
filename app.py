from pymongo import MongoClient
from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps,loads
from flask.ext.jsonpify import jsonify
from bson import json_util, ObjectId

client = MongoClient('mongodb://test:test@ds123725.mlab.com:23725/ar')
db = client['ar']
collectionLocations = db['Locations']
collectionUsers = db['Users']

app = Flask(__name__)
api = Api(app)

class Locations(Resource):
    def get(self,latitude=None,longtitude=None):
        if latitude is None :
            return 'ใส่พิกัดมาด้วยโว้ย /search=[latitude],[longtitude]'
        locations = collectionLocations.find()
        for location in locations :
            if Locations.calculateHaversine(latitude,longtitude,location['Latitude'],location['Longtitude'])>5:
                locations.remove(location)
        result = {'locations': [
            Locations.idToString(location) for location in locations]}
        latitude = float(latitude)
        longtitude = float(longtitude)
        return result
    def calculateHaversine(lat1, lon1, lat2, lon2):
        r = 6372.797560856
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        return c * r
    def idToString(location):
        location['id'] = str(location['_id'])
        del location['_id']
        return loads(json_util.dumps(location))

class Rate(Resource):
    def post(self):
        username = request.form['username']
        locationId = request.form['locationId']
        rating = request.form['rating']
        collectionLocations.update_one({'_id' : ObjectId(locationId)},{'$set':rating,'$push':{'RatedUser': username}})

class Comment(Resource):
    def post(self):
        comment = request.form['comment']
        locationId = request.form['locationId']
        collectionLocations.update_one({'_id' : ObjectId(locationId)},{'$push':{'Comments': comment}})

class Report(Resource):
    def post(self):
        username = request.form['username']
        type = request.form['type']
        detail = request.form['detail']
        locationId = request.form['locationId']
        collectionLocations.update_one({'_id' : ObjectId(locationId)},{'$push':{'Reports': {'Type':type,'Detail':detail,'ReportedBy':username}}})
        
class AddLocation(Resource):
    def post(self):
        name = request.form['name']
        category = request.form['category']
        latitude = request.form['latitude']
        longtitude = request.form['longtitude']
        urlPic = request.form['urlPic']
        collectionLocations.insert_one({
            'Name':name,
            'Category':category,
            'Latitude':latitude,
            'Longtitude':longtitude,
            'Rating':0,
            'RatedUser':[],
            'URLPic':urlPic,
            'Comments':[],
            'Reports':[]})

class Login(Resource):
    def post(self):
        collectionUsers.insert_one({
            'Username':request.form['username']})

api.add_resource(Locations,'/search', '/search=<latitude>,<longtitude>')
api.add_resource(Rate, '/rate')
api.add_resource(Comment, '/comment')
api.add_resource(Report, '/report')
api.add_resource(AddLocation, '/addlocation')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(host='127.0.0.1',debug=True)
