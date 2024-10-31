# BOOKING SERVICE

#ALLOWS FOR CREATING A NEW BOOKING - ALSO CHECKS FOR AVAILABILITY AND SUCH

from flask import Flask, jsonify, request
import requests
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/book/room', methods=["POST"])
def create_room_booking():

    # Retrieve the data [Room Number, Guest Id, Room Price per day, Days Rented, Season]
    data = request.json
    room_number = data.get("room_number")
    guest_id = data.get("guest_id")
    rented_days = data.get("days_rented")
    season = data.get("season")
    number_of_guests = data.get("number_of_guests")
    start_date = data.get("start_date")




    #Other microservices
    rooms_service_api = "http://room-service:5000/room/availability"
    rooms_service_room_type = f"http://room-service:5000/room/type/{room_number}"
    
    #GET ROOM TYPE
    room_type_response = requests.get(rooms_service_room_type)
    if room_type_response.status_code == 400:
        return "Couldnt find room"
    room_type = room_type_response.text
        
    #GET
    room_pricing_service = f"http://room-pricing-service:5000/rooms/{room_type}/{season}"
    pricing_response = requests.get(room_pricing_service)
    if room_type_response.status_code == 404:
        return "Couldnt find price", 404
    
    if pricing_response.status_code != 200:
        return "Unable to retrieve price", 500
    
    pricing_response_data = pricing_response.json()

    daily_price = pricing_response_data.get("daily_price")


    #Calculate pricing 

    total_price = daily_price * rented_days

    # Calculate end date
    date_parts = start_date.split('/')
    year = int(date_parts[0])
    month = int(date_parts[1])
    day = int(date_parts[2])

    date = datetime(year,month,day)

    end_date = date + timedelta(days=rented_days)

    # Create the request body - CHECK AVAILABILITY
    request_body = {"room_number": room_number}
    response = requests.get(rooms_service_api, params = request_body)
    response_data = response.json()

    #Check the status of the response
    if response.status_code == 200 and response_data == True:
        #The room is available for booking
        with sqlite3.connect("/app/data/bookings.db") as conn:
            cur = conn.cursor()
            cur.execute(""" INSERT INTO bookings
                        (
                        days_rented,
                        season,
                        price,
                        room_number,
                        guest_id,
                        number_of_guests,
                        start_date,
                        end_date
                        ) VALUES (?,?,?,?,?,?,?,?)""", (rented_days, season, total_price, room_number, guest_id, number_of_guests,start_date,end_date,))
            conn.commit()
            #Update the availability in the rooms microservice
    
            requests.put("http://room-service:5000/room/availability", json={"room_number": room_number})
            # Maybe some error handling idk?

    
@app.route('/bookings', methods=["GET"])
def see_all_bookings(): 
    # Connect to the database
    with sqlite3.connect("/app/data/bookings.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM bookings")
        data = cur.fetchall()
  
        #Check the response
        if not data:
            #response is empty
            return "There was an error trying to retrieve all bookings!", 400
        else:
            bookings = []

            for booking in data:
                booking_format = {
                    "booking_id": booking[0],
                    "days_rented": booking[1],
                    "season": booking[2],
                    "price": booking[3],
                    "room_number": booking[4],
                    "guest_id": booking[5],
                    "number_of_guests": booking[6],
                    "start_date": booking[7],
                    "end_date": booking[8]
                    }
                bookings.append(booking_format)

            # Return the list of bookings as JSON
            return jsonify(bookings), 200
        
#Endpoint for removing a booking
@app.route('/book/room/<int:booking_id>', methods=["DELETE"])
def delete_booking(booking_id):
    with sqlite3.connect("/app/data/bookings.db") as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM bookings WHERE booking_id = ? ",(booking_id,))

        if cur.rowcount == 0:
            return "Booking not found - Couldnt remove booking", 400
        
        return "Booking removed successfully", 200
    
#Send all data
@app.route('/booking/data', methods=["GET"])
def get_bookings_data():
    with sqlite3.connect('/app/data/bookings.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM bookings")
        data = cur.fetchall()

        #Check the response
        if not data:
            #response is empty
            return "There was an error trying to retrieve all bookings!", 400
        return data, 200


        

    
app.run(debug=True, host="0.0.0.0")