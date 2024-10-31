# Booking Service

This Flask-based microservice allows for creating a new booking and checks for room availability.

## Endpoints

- **Create a new booking**

    - **URL**: `/book/room`
    - **Method**: `POST`
    - **Description**: Creates a new room booking after checking availability.
    - **Request Body**:

        ```json
        {
            "room_number": 101,
            "guest_id": 1,
            "days_rented": 3,
            "season": "peak",
            "number_of_guests": 2,
            "start_date": "2024/11/01"
        }
        ```

    - **Response**:
        - `201 Created`: Booking created successfully.
        - `400 Bad Request`: Could not find room or retrieve price.

- **Get all bookings**

    - **URL**: `/bookings`
    - **Method**: `GET`
    - **Description**: Retrieves a list of all bookings.
    - **Response**:
        - `200 OK`: Returns a list of bookings in JSON format.

- **Delete a booking**

    - **URL**: `/book/room/<booking_id>`
    - **Method**: `DELETE`
    - **Description**: Deletes a specific booking by ID.
    - **Response**:
        - `200 OK`: Booking removed successfully.
        - `400 Bad Request`: Booking not found.

- **Get booking data**

    - **URL**: `/booking/data`
    - **Method**: `GET`
    - **Description**: Retrieves raw booking data.
    - **Response**:
        - `200 OK`: Returns booking data.
        - `400 Bad Request`: Error retrieving booking data.
