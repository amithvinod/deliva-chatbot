
# **Deliva Project - Flight Booking Bot**

Deliva is an intelligent **flight booking bot** designed to handle various tasks related to flight bookings. It integrates features such as checking flight availability, retrieving price calendars, saving user details for booking, and even performing dummy bookings with dummy tickets. All flight-related information in this bot is specifically focused on **domestic flights within India**.

---

## **Features**
- **Flight Booking**: Book flights seamlessly using the bot.
- **Check Flight Availability**: Use free APIs from **RapidAPI** to check flight availability.
- **Price Calendar**: Get flight prices across different dates to help users make informed decisions.
- **Save User Details**: Store and manage user details for bookings.
- **Search Airports**: Find airports near a given city to get the best flight options.
- **Dummy Booking**: Make a dummy flight booking and generate dummy tickets.
- **Flight Scraper API**: The bot uses the **Flight Scraper API** from RapidAPI to make the calls and fetch details.

---

## **Project Structure**
```
Deliva/
├── backend/               # Backend project folder (FastAPI)
├── frontend/              # Frontend project folder (Flutter)
├── README.md              # Project documentation
```

---

## **Setup Instructions**

### **1. Prerequisites**
- Install **Python 3.9+** for the backend.
- Install **Flutter** for the frontend.
- Install **PostgreSQL** for the database.

---

### **2. Backend Setup**
The backend is built with **FastAPI**. Follow these steps to set it up locally:

#### **Steps to Run Locally:**
1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate     # For Windows
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `const.py` file in the `backend` folder:
   ```plaintext
   DATABASE_URL = "your-database-url"
   API_KEY = "your-api-key"
   SECRET_KEY = "your-secret-key"
   FLIGHT_SCRAPER_API_KEY = "your-rapidapi-key"
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

6. Access the API locally at `http://127.0.0.1:8000`.

---

### **3. Frontend Setup**
The frontend is built with **Flutter**. Follow these steps to set it up locally:

#### **Steps to Run Locally:**
1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```

2. Create a `const.dart` file in the `lib` folder:
   ```dart
   const String cloudProjectId = "your-cloud-project-id";
   const String apiKey = "your-api-key";
   ```

3. Create an `assets` folder in the root directory:
   ```plaintext
   frontend/
   ├── assets/
   │   └── service_account.json
   ```

4. Add the `assets` folder to `pubspec.yaml`:
   ```yaml
   flutter:
     assets:
       - assets/service_account.json
   ```

5. Run the Flutter application:
   ```bash
   flutter run
   ```

---

## **Environment Files**
To avoid exposing sensitive information, sensitive details like API keys and database URLs are stored in environment files:

- **Backend**: Add sensitive information to `const.py` (e.g., database URL, API keys).
- **Frontend**: Add credentials to `const.dart` and service account files in `assets`.

---

## **File Exclusion**
Make sure to exclude sensitive files before committing to version control:
- Use a `.gitignore` file with the following rules:
  ```plaintext
  # Backend
  backend/const.py
  backend/__pycache__/  

  # Frontend
  frontend/assets/service_account.json
  frontend/lib/const.dart
  ```

---

## **Contributing**
1. Fork the repository.
2. Create a new branch for your feature:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature description"
   ```
4. Push your changes:
   ```bash
   git push origin feature-name
   ```
5. Create a pull request.

---

## **License**
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## **Contact**
For any inquiries or issues, feel free to reach out:
- **Email**: amithvinodd@gmail.com
- **GitHub**: [Your GitHub Profile](https://github.com/amithvinod)
