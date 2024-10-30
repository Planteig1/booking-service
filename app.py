# BOOKING SERVICE

#ALLOWS FOR CREATING A NEW BOOKING - ALSO CHECKS FOR AVAILABILITY AND SUCH

from flask import Flask, jsonify, request
import requests
import sqlite3

app = Flask(__name__)

@app.route('/book/room', methods=["POST"])
def create_room_booking():

    # Retrieve the data [Room Number, Guest Id, Room Price per day, Days Rented, Season]
    data = request.json
    room_number = data.get("room_number")
    guest_id = data.get("guest_id")
    rented_days = data.get("days_rented")
    season = data.get("season")

    price_daily = data.get("daily_price")
    total_price = price_daily * rented_days

    #Other microservices
    rooms_service_api = "http://room-service:5000/room/availability"

    # Create the request body
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
                        guest_id
                        ) VALUES (?,?,?,?,?)""", (rented_days, season, total_price, room_number, guest_id,))
            conn.commit()
            #Update the availability in the rooms microservice
    
            requests.put("http://room-service:5000/room/availability", json={"room_number": room_number})
            # Maybe some error handling idk?
            return "Room booked successfully", 200
    elif response.status_code == 200 and response_data == False: 
        # Good response, but the room is already booked!
        return "Room is already booked", 400
    else:
        # Bad response
        return "Oh no! Something went wrong, please try again later!", 400
    
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
                    "guest_id": booking[5]
                    }
                bookings.append(booking_format)

            # Return the list of bookings as JSON
            return jsonify(bookings), 200
        
#Endpoint for removing a booking
@app.route('/book/room/<int:booking_id>', mehtods=["DELETE"])

def delete_booking(booking_id):
    with sqlite3.connect("/app/data/bookings.db") as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM bookings WHERE booking_id = ? ",(booking_id,))

        if cur.rowcount == 0:
            return "Booking not found", 400
        
        return "Booking successfull", 200

        

    
app.run(debug=True, host="0.0.0.0")