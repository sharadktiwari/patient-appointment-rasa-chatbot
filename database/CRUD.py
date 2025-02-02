import pymongo
import os

# MONGO_URL = os.getenv("MONGO_URL")
# DB_NAME = os.getenv("DB_NAME")

MONGO_URL = "mongodb+srv://sharadkumartiwari1508:171489956@clustor0.kyc0e.mongodb.net/?retryWrites=true&w=majority&appName=clustor0"
DB_NAME = "appointease"

client = pymongo.MongoClient(MONGO_URL)
database = client[DB_NAME]

doc_loc_details = database["doc_location_details"]
doc_details = database["doc_details"]
patient_details = database["patient_details"]
appointment_details = database["appointment_details"]
patient_history = database["patient_history"]


class dboperations:
    def check_doc_presence(dr_contact:str):
        try:
            doc_id = doc_details.find_one({"contact":dr_contact},['doc_id'])
            if doc_id:
                return {'status_code':200,'data':doc_id['doc_id']}
            else:
                return {'status_code':400,'data':'Doctor data not found'}
        except Exception as e:
            print(e)
            return {'status_code':400,'data':'Data Fetching Failed'}

    def get_doc_locations(dr_contact:str,only_loc_ids:bool=False) -> dict:
        try:
            doc_id = doc_details.find_one({"contact":dr_contact},['doc_id'])
            if doc_id:
                if only_loc_ids:
                    loc_data = doc_loc_details.find({'doc_id':doc_id['doc_id']},['loc_id'])
                    if loc_data:
                        return {'status_code':200,'data':[data['loc_id'] for data in loc_data]}
                    else:
                        return {'status_code':400,'data':'Location data not found'}
                else:
                    loc_data = doc_loc_details.find({'doc_id':doc_id['doc_id']},['loc_id','loc_address'])
                    if loc_data:
                        return {'status_code':200,'data':[data for data in loc_data]}
                    else:
                        return {'status_code':400,'data':'Location data not found'}
            else:
                return {'status_code':400,'data':'Doctor data not found'}
        except Exception as e:
            print(e)
            return {'status_code':400,'data':'Data Fetching Failed'}
        
    
    def get_appointment_details(visit_id:str):
        try:
            app_details = appointment_details.find_one({"visit_id":visit_id,'status': {"$in":[1,2]}})
            if app_details:
                pat_details = patient_details.find_one({'patient_id':app_details['patient_id']},['name'])
                pat_history = patient_history.find_one({'patient_id':app_details['patient_id'], "history.visit_id": visit_id},{'history.$':1})
                if pat_history:
                    pat_details['history'] = pat_history['history'][-1]
                loc_details = doc_loc_details.find_one({'loc_id':app_details['loc_id']},['doc_id','loc_address'])
                if pat_details and loc_details:
                    app_details.update(pat_details)
                    app_details.update(loc_details)
                    doc_dets = doc_details.find_one({'doc_id':loc_details['doc_id']},['name'])
                    if doc_dets:
                        doc_dets['doc_name'] = doc_dets.pop('name')
                        app_details.update(doc_dets)
                        return {'status_code':200,'data':app_details}
                    else:
                        return {'status_code':400,'data':'Doctor data not found'}
                else:
                    return {'status_code':400,'data':'Patient and Location data not found'}
            else:
                return {'status_code':400,'data':'Appointment data not found'}
        except Exception as e:
            print(e)
            return {'status_code':400,'data':'Data Fetching Failed'}


    def location_appointment_days(loc_id:str) -> dict:
        try:
            appointment_days = doc_loc_details.find_one({"loc_id":loc_id},['avail_days'])
            if appointment_days:
                return {'status_code':200,'data':appointment_days['avail_days']}
            else:
                return {'status_code':400,'data':'Location data not found'}
        except Exception as e:
            print(e)
            return {'status_code':400,'data':'Data Fetching Failed'}
        
    
    def location_appointment_time(loc_id:str) -> dict:
        try:
            appointment_time_slots = doc_loc_details.find_one({"loc_id":loc_id},['avail_time_slots'])
            if appointment_time_slots:
                return {'status_code':200,'data':appointment_time_slots['avail_time_slots']}
            else:
                return {'status_code':400,'data':'Location data not found'}
        except Exception as e:
            print(e)
            return {'status_code':400,'data':'Data Fetching Failed'}        
        

    def check_user_presence(data:dict) -> dict:
        try:
            data_present = patient_details.find_one(data)
            if not data_present:
                return {'status_code':404,'data':'User Not Found'}
            else:
                return {'status_code':200,'data':data_present}
        except Exception as e:
            print(e)
            return {'status_code':400,'data':'Data Insertion Failed'}
        

    def fill_patient_data(data:dict) -> dict:
        try:
            data_present = patient_details.find_one({
                                                    "name":data['name'].lower(),
                                                    "contact":data['contact']
                                                    })
            if not data_present:
                patient_details.insert_one(data)
                return {'status_code':404,'data':data['patient_id']}
            else:
                return {'status_code':200,'data':data_present['patient_id']}
        except Exception as e:
            print(e)
            return {'status_code':400,'data':'Data Insertion Failed'}
        
    
    def fill_appointment_data(data:dict) -> dict:
        try:
            data_present = appointment_details.find_one({
                                                    "patient_id":data['patient_id'],
                                                    "loc_id": data['loc_id'],
                                                    "app_date": data['app_date'],
                                                    "app_time_slot": data['app_time_slot'],
                                                    "status": {'$in':[1,2]}
                                                    })
            if not data_present:
                appointment_details.insert_one(data)
                return {'status_code':404,'data':data['visit_id']}
            else:
                return {'status_code':200,'data':data_present['visit_id']}
        except Exception as e:
            print(e)
            return {'status_code':400,'data':'Data Insertion Failed'}


    def fill_patient_history(patient_id:str,data:dict,insertion_time) -> dict:
        try:
            data_present = patient_history.find_one({
                                                    "patient_id":patient_id
                                                    })
            if not data_present:
                patient_history.insert_one({'patient_id':patient_id, 'history':[data], "created_at": insertion_time, "updated_at": insertion_time})
                return {'status_code':201,'data':patient_id}
            else:
                patient_history.update_one({'patient_id':patient_id},{'$push':{'history':data}, "$set":{'updated_at':insertion_time}})
                return {'status_code':200,'data':patient_id}
        except Exception as e:
            print(e)
            return {'status_code':400,'data':'Data Insertion Failed'}
        
    
    def update_appointment(visit_id:str,app_date:str,app_time:str, insertion_time) -> dict:
        try:
            appointment_details.update_one({'visit_id':visit_id},{"$set":{'app_date':app_date,'app_time_slot':app_time, 'updated_at':insertion_time}})
            return {'status_code':200,'data':'Appointment Updated'}
        except Exception as e:
            print(e)
            return {'status_code':400,'data':'Data Updation Failed'}
        
    
    def update_status(visit_id:str,status:int, insertion_time) -> dict:
        try:
            appointment_details.update_one({'visit_id':visit_id},{"$set":{'status':status, 'updated_at':insertion_time}})
            return {'status_code':200,'data':'Appointment Updated'}
        except Exception as e:
            print(e)
            return {'status_code':400,'data':'Data Updation Failed'}
        
    
    def get_patient_appointments(dr_contact,contact,curr_time):
        try:
            loc_ids = dboperations.get_doc_locations(dr_contact,True)
            if loc_ids['status_code']==400:
                return {'status_code':404,'data':"Appointment Details Not Found"}
            
            patient_data = patient_details.find({
                                        "contact":contact
                                        },['name','patient_id'])

            if not patient_data:
                return {'status_code':404,'data':'Patient Not Found'}
            
            patient_data = {pids['patient_id']:pids['name'] for pids in patient_data}

            scheduled_appointments = appointment_details.find({
                                        "patient_id":{'$in':list(patient_data.keys())},
                                        "loc_id" : {'$in':loc_ids['data']},
                                        "status": {'$in':[1,2]},
                                        "app_date": {'$gte':curr_time}
                                        },
                                        ['visit_id','loc_id','app_date','app_time_slot','patient_id'])
            
            if not scheduled_appointments:
                return {'status_code':404,'data':'Appointment Not Found'}

            appointment_data = []
            for data in scheduled_appointments:
                data['loc_address'] = doc_loc_details.find_one({'loc_id':data['loc_id']},['loc_address'])['loc_address']
                data['name'] = patient_data[data['patient_id']]
                del data['_id']
                appointment_data.append(data)

            if not appointment_data:
                return {'status_code':404,'data':"Appointment Details Not Found"}
            else:
                return {'status_code':200,'data':appointment_data}
        except Exception as e:
            print(e)
            return {'status_code':400,'data':'Data Fetching Failed'}
