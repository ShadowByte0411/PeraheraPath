# PeraharaPath - Smart Festival Routing for Sri Lanka
PeraharaPath is an intelligent route planning application designed to navigate the unique traffic challenges presented by Sri Lanka's vibrant cultural festivals. It provides optimal, data-driven travel routes by factoring in festival schedules, road closures, and dynamic congestion levels.

## About The Project
Navigating Sri Lanka during festival seasons can be challenging due to unpredictable traffic and road closures. PeraharaPath was created to solve this problem. It uses a custom-built database of festivals and a festival-aware A\* search algorithm to calculate the fastest route for travelers, providing realistic estimates and clear warnings.
This project empowers users to make informed travel decisions, avoiding delays and enjoying the cultural richness of Sri Lanka without the stress of navigating through festival congestion.

### Key Features
  * **📍 Map-Based Route Planning:** Computes the fastest path between any two districts using an A\* search algorithm.
  * **⚠️ Dynamic Disruption Warnings:** Alerts users to potential delays by factoring in active festivals, road closures, and real-time congestion estimates.
  * **💰 Real-World Cost Estimation:** Calculates estimated travel time, total distance, and fuel expenses for the journey.
  * **🕌 Cultural Data Integration:** Utilizes a centralized JSON database of major Sri Lankan festivals, their schedules, and their impact on traffic.
  * **🖥️ User-Friendly Visualization:** Provides an intuitive web interface for planning trips and visualizing the final route and warnings on an interactive map.

## Technology Stack
This project is built with a modern, lightweight technology stack:
  * **Backend:** **Python** with the **Flask** framework
  * **Frontend:** **HTML5**, **CSS3**, and vanilla **JavaScript**
  * **Mapping Library:** **Leaflet.js** for interactive map visualization
  * **Data Storage:** **JSON** for the festival and road network database

## Getting Started
Follow these instructions to get a local copy of PeraharaPath up and running.

### Prerequisites
You will need **Python 3.7+** and **pip** installed on your system.

### Installation
1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/PeraharaPath.git
    ```

2.  **Navigate to the project directory:**
    ```sh
    cd PeraharaPath
    ```

3.  **Create and activate a virtual environment** (Recommended):
      * On Windows:
        ```sh
        python -m venv venv
        .\venv\Scripts\activate
        ```
      * On macOS/Linux:
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```

4.  **Install the dependencies:**
    First, create a file named `requirements.txt` in the main project folder and add the following line to it:
    ```
    Flask
    ```

    Then, run the installation command:
    ```sh
    pip install -r requirements.txt
    ```

### Usage
1.  **Run the Flask application:**
    ```sh
    python app.py
    ```

2.  **Open your web browser** and navigate to:
    ```
    http://127.0.0.1:5000
    ```

The PeraharaPath application should now be running locally\!
