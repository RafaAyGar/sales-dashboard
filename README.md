# :bar_chart: Sales Analysis and Forecasting Dashboard

A full-stack data analytics project that integrates data processing, predictive modeling, and interactive visualization. Historical sales data is cleaned and stored in a database, analyzed for trends, and used to train a simple predictive model (ARIMA) to forecast future sales. An interactive dashboard built with Streamlit and Plotly displays key insights, trends, and forecasts, and can be deployed to the cloud for public access.

<br>

<p align="center">
    <img src="https://raw.githubusercontent.com/RafaAyGar/sales-dashboard/main/docs/scheme-project-sales-dashboard.png" width="50%" alt="Project scheme" /></a>
</p>
<br>

:computer: Tech Stack:

* Data: Pandas, NumPy, SQLAlchemy.

* Modeling: Statsmodels.

* Visualization: Plotly, Streamlit.

* Infrastructure: PostgreSQL, Docker.
<br>

:books: This project consists of four Dockerized modules:

* ``database``: A PostgreSQL database that stores all project data.

* ``sales-manager``: Handles the insertion and updating of sales records in ``database``.

* ``forecasts``: Uses the stored sales data to train machine learning models and generate forecasts.

* ``dashboard``: A Streamlit-based Python dashboard that visually presents sales and forecast information.

These four modules interact in real time. The Sales Manager periodically inserts new sales data into the ``database``. The ``forecasts`` module regularly checks for new entries. When new data is available, it retrains an ARIMA model and generates updated forecasts. The ``Dashboard`` continuously reads the data and presents it in a clear, visually engaging format.

<br>

:arrow_forward: Deployment
Fast build up and run the project:
```
docker-compose up -d --build
```
Access the dashboard: From the host machine, go to:
```
http://localhost:8501/
```


