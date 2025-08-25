<p align="center">
    <img src="https://raw.githubusercontent.com/RafaAyGar/sales-dashboard/main/docs/scheme-project-sales-dashboard.png" width="50%" alt="Project scheme" /></a>
</p>


This project consists of four Dockerized modules:

* database: A PostgreSQL database that stores all project data.

* sales-manager: Handles the insertion and updating of sales records in the database.

* forecasts: Uses the stored sales data to train machine learning models and generate forecasts.

* dashboard: A Streamlit-based Python dashboard that visually presents sales and forecast information.

These four modules interact in real time. The Sales Manager periodically inserts new sales data into the database. The Forecasts module regularly checks for new entries. When new data is available, it retrains an ARIMA model and generates updated forecasts. The Dashboard continuously reads the data and presents it in a clear, visually engaging format.