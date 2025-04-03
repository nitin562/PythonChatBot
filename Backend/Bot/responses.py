from flask import jsonify
def success(status,type,payload):
    return jsonify({
        "success":True,
        "status":status,
        "type":type,
        "payload":payload
    })

def error(status,type,error):
    return jsonify({
        "success":False,
        "status":status,
        "type":type,
        "payload":error
    })