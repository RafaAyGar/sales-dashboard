CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT,
    operation TEXT,
    operation_time TIMESTAMP DEFAULT NOW(),
    user_name TEXT,
    row_data JSONB
);

CREATE OR REPLACE FUNCTION log_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log(table_name, operation, user_name, row_data)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, row_to_json(OLD));
        RETURN OLD;
    ELSE
        INSERT INTO audit_log(table_name, operation, user_name, row_data)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, row_to_json(NEW));
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sales_audit
AFTER INSERT OR UPDATE OR DELETE
ON sales_db
FOR EACH ROW EXECUTE FUNCTION log_changes();
