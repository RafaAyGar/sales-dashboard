CREATE TABLE forecasts (
    "model" VARCHAR(32),
    "trained_at" TIMESTAMP WITHOUT TIME ZONE,
    "hyperparams" VARCHAR(128),
    "n_training_days" INT,
    "last_training_date" TIMESTAMP WITHOUT TIME ZONE,
    "forecast_date" TIMESTAMP WITHOUT TIME ZONE,
    "predicted_total_amount" REAL
);

