# Vehicle Rental Management System (VRMS)

A simple web-based application for managing a vehicle rental business.

## Features

*   **Dashboard:** View the overall status of the vehicle fleet.
*   **Vehicles:** Add and view vehicle information.
*   **Customers:** Manage customer data.
*   **Reservations:** Create and manage vehicle reservations.
*   **Maintenance:** Track vehicle maintenance records.

## How to Run

1.  **Install Dependencies:**

    This project requires Python and Flask. Install Flask using pip:

    ```bash
    pip install Flask
    ```

2.  **Initialize the Database:**

    The `database.py` script creates the SQLite database file (`vrms.db`) and populates it with sample data. Run this script first:

    ```bash
    python database.py
    ```

3.  **Run the Application:**

    Start the Flask development server:

    ```bash
    python app.py
    ```

    The application will be accessible at `http://127.0.0.1:5000` in your web browser.