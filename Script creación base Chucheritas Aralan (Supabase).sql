-- ============================================================
--  CHUCHERITAS ARALAN — Supabase / PostgreSQL
--  Order: 1) Schemas  2) Tables  3) Indexes, Views,
--          Triggers, Functions  4) RLS  5) Seed
-- ============================================================


-- ============================================================
-- 1. SCHEMAS
-- ============================================================

CREATE SCHEMA IF NOT EXISTS hr;
CREATE SCHEMA IF NOT EXISTS products;
CREATE SCHEMA IF NOT EXISTS clients;
CREATE SCHEMA IF NOT EXISTS orders;


-- ============================================================
-- 2. TABLES
-- ============================================================

-- ------------------------------------------------------------
-- hr.jobs
-- ------------------------------------------------------------
CREATE TABLE hr.jobs (
    job_id      SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    level       INTEGER      NOT NULL DEFAULT 1
                    CHECK (level IN (1, 2)),   -- 1: delivery, 2: admin
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- hr.employees
-- ------------------------------------------------------------
CREATE TABLE hr.employees (
    employee_id     SERIAL PRIMARY KEY,
    auth_id         UUID         UNIQUE REFERENCES auth.users(id) ON DELETE SET NULL,
    job_id          INTEGER      NOT NULL REFERENCES hr.jobs(job_id)
                        ON DELETE RESTRICT ON UPDATE CASCADE,
    name            VARCHAR(100) NOT NULL,
    phone           VARCHAR(20)  NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    status          VARCHAR(10)  NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'inactive')),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- products.categories
-- ------------------------------------------------------------
CREATE TABLE products.categories (
    category_id     CHAR(3)      PRIMARY KEY,
    description     VARCHAR(100) NOT NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- products.products
-- ------------------------------------------------------------
CREATE TABLE products.products (
    product_id      SERIAL          PRIMARY KEY,
    category_id     CHAR(3)         NOT NULL REFERENCES products.categories(category_id)
                        ON DELETE RESTRICT ON UPDATE CASCADE,
    name            VARCHAR(100)    NOT NULL,
    description     VARCHAR(255)    NOT NULL,
    price           NUMERIC(10,2)   NOT NULL CHECK (price > 0),
    stock           INTEGER         NOT NULL DEFAULT 0 CHECK (stock >= 0),
    status          VARCHAR(15)     NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'discontinued')),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- products.product_pictures
-- ------------------------------------------------------------
CREATE TABLE products.product_pictures (
    picture_id      SERIAL  PRIMARY KEY,
    product_id      INTEGER NOT NULL REFERENCES products.products(product_id)
                        ON DELETE CASCADE ON UPDATE CASCADE,
    picture_url     TEXT    NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- clients.clients
-- ------------------------------------------------------------
CREATE TABLE clients.clients (
    client_id       SERIAL PRIMARY KEY,
    auth_id         UUID         UNIQUE REFERENCES auth.users(id) ON DELETE SET NULL,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    phone           VARCHAR(20)  NOT NULL,
    status          VARCHAR(10)  NOT NULL DEFAULT 'active'
                        CHECK (status IN ('active', 'suspended')),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- clients.delivery_addresses
-- ------------------------------------------------------------
CREATE TABLE clients.delivery_addresses (
    address_id      SERIAL PRIMARY KEY,
    client_id       INTEGER      NOT NULL REFERENCES clients.clients(client_id)
                        ON DELETE CASCADE ON UPDATE CASCADE,
    name            VARCHAR(100) NOT NULL,
    street          VARCHAR(100) NOT NULL,
    zip_code        CHAR(5)      NOT NULL CHECK (zip_code ~ '^\d{5}$'),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- orders.orders
-- ------------------------------------------------------------
CREATE TABLE orders.orders (
    order_id        SERIAL PRIMARY KEY,
    client_id       INTEGER         NOT NULL REFERENCES clients.clients(client_id)
                        ON DELETE RESTRICT ON UPDATE CASCADE,
    address_id      INTEGER         NOT NULL REFERENCES clients.delivery_addresses(address_id)
                        ON DELETE RESTRICT ON UPDATE CASCADE,
    deliverer_id    INTEGER         NOT NULL REFERENCES hr.employees(employee_id)
                        ON DELETE RESTRICT ON UPDATE CASCADE,
    delivery_date   DATE            NOT NULL,
    total_amount    NUMERIC(10,2)   NOT NULL CHECK (total_amount > 0),
    status          VARCHAR(15)     NOT NULL DEFAULT 'processing'
                        CHECK (status IN ('processing','on_the_way','delivered','cancelled')),
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- orders.order_details
-- ------------------------------------------------------------
CREATE TABLE orders.order_details (
    order_id    INTEGER         NOT NULL REFERENCES orders.orders(order_id)
                    ON DELETE CASCADE ON UPDATE CASCADE,
    product_id  INTEGER         NOT NULL REFERENCES products.products(product_id)
                    ON DELETE RESTRICT ON UPDATE CASCADE,
    quantity    INTEGER         NOT NULL CHECK (quantity > 0),
    subtotal    NUMERIC(10,2)   NOT NULL CHECK (subtotal > 0),

    PRIMARY KEY (order_id, product_id)
);


-- ============================================================
-- 3A. INDEXES
-- ============================================================

CREATE INDEX idx_products_category     ON products.products(category_id);
CREATE INDEX idx_products_status       ON products.products(status);
CREATE INDEX idx_orders_client         ON orders.orders(client_id);
CREATE INDEX idx_orders_deliverer      ON orders.orders(deliverer_id);
CREATE INDEX idx_orders_status         ON orders.orders(status);
CREATE INDEX idx_order_details_product ON orders.order_details(product_id);


-- ============================================================
-- 3B. HELPER FUNCTIONS (used by RLS policies)
-- ============================================================

-- Returns true if the current user is a client
CREATE OR REPLACE FUNCTION clients.is_client()
RETURNS BOOLEAN LANGUAGE sql SECURITY DEFINER STABLE AS $$
    SELECT EXISTS (
        SELECT 1 FROM clients.clients
        WHERE auth_id = auth.uid()
          AND status  = 'active'
    );
$$;

-- Returns the client_id for the current user
CREATE OR REPLACE FUNCTION clients.current_client_id()
RETURNS INTEGER LANGUAGE sql SECURITY DEFINER STABLE AS $$
    SELECT client_id FROM clients.clients
    WHERE auth_id = auth.uid()
    LIMIT 1;
$$;

-- Returns true if the current user is an active employee
CREATE OR REPLACE FUNCTION hr.is_employee()
RETURNS BOOLEAN LANGUAGE sql SECURITY DEFINER STABLE AS $$
    SELECT EXISTS (
        SELECT 1 FROM hr.employees
        WHERE auth_id = auth.uid()
          AND status  = 'active'
    );
$$;

-- Returns the job level for the current user (NULL if not an employee)
CREATE OR REPLACE FUNCTION hr.current_level()
RETURNS INTEGER LANGUAGE sql SECURITY DEFINER STABLE AS $$
    SELECT j.level
    FROM hr.employees e
    JOIN hr.jobs j ON e.job_id = j.job_id
    WHERE e.auth_id = auth.uid()
      AND e.status  = 'active'
    LIMIT 1;
$$;

-- Returns the employee_id for the current user
CREATE OR REPLACE FUNCTION hr.current_employee_id()
RETURNS INTEGER LANGUAGE sql SECURITY DEFINER STABLE AS $$
    SELECT employee_id FROM hr.employees
    WHERE auth_id = auth.uid()
    LIMIT 1;
$$;


-- ============================================================
-- 3C. STOCK TRIGGER
-- ============================================================

-- Decrease stock when an order_detail is inserted
CREATE OR REPLACE FUNCTION orders.decrease_stock()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
DECLARE
    v_stock INTEGER;
BEGIN
    -- Lock the product row to prevent concurrent overselling
    SELECT stock INTO v_stock
    FROM products.products
    WHERE product_id = NEW.product_id
    FOR UPDATE;

    IF v_stock < NEW.quantity THEN
        RAISE EXCEPTION
            'Insufficient stock for product %. Available: %, Requested: %',
            NEW.product_id, v_stock, NEW.quantity;
    END IF;

    UPDATE products.products
       SET stock = stock - NEW.quantity
     WHERE product_id = NEW.product_id;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_decrease_stock
BEFORE INSERT ON orders.order_details
FOR EACH ROW EXECUTE FUNCTION orders.decrease_stock();

-- Restore stock when an order is cancelled
CREATE OR REPLACE FUNCTION orders.restore_stock()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    -- Only act when status changes TO 'cancelled'
    IF NEW.status = 'cancelled' AND OLD.status <> 'cancelled' THEN
        UPDATE products.products p
           SET stock = stock + od.quantity
          FROM orders.order_details od
         WHERE od.order_id  = OLD.order_id
           AND p.product_id = od.product_id;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_restore_stock
AFTER UPDATE OF status ON orders.orders
FOR EACH ROW EXECUTE FUNCTION orders.restore_stock();


-- ============================================================
-- 3D. STATS VIEWS (admin only via RLS)
-- ============================================================

-- Today's sales
CREATE OR REPLACE VIEW orders.v_today_sales AS
SELECT
    COUNT(*)                        AS total_orders,
    COALESCE(SUM(total_amount), 0)  AS revenue
FROM orders.orders
WHERE created_at >= CURRENT_DATE
  AND created_at <  CURRENT_DATE + INTERVAL '1 day'
  AND status     <> 'cancelled';

-- Top 10 best-selling products (all time)
CREATE OR REPLACE VIEW orders.v_top_products AS
SELECT
    p.product_id,
    p.name,
    SUM(od.quantity)                AS units_sold,
    SUM(od.subtotal)                AS total_revenue
FROM orders.order_details od
JOIN products.products p ON od.product_id = p.product_id
JOIN orders.orders     o ON od.order_id   = o.order_id
WHERE o.status <> 'cancelled'
GROUP BY p.product_id, p.name
ORDER BY units_sold DESC
LIMIT 10;


-- ============================================================
-- 4. ROW LEVEL SECURITY (RLS)
-- ============================================================

-- Enable RLS on every table
ALTER TABLE hr.jobs                         ENABLE ROW LEVEL SECURITY;
ALTER TABLE hr.employees                    ENABLE ROW LEVEL SECURITY;
ALTER TABLE products.categories             ENABLE ROW LEVEL SECURITY;
ALTER TABLE products.products               ENABLE ROW LEVEL SECURITY;
ALTER TABLE products.product_pictures       ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients.clients                 ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients.delivery_addresses      ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders.orders                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders.order_details            ENABLE ROW LEVEL SECURITY;

-- ------------------------------------------------------------
-- products.categories — anon + authenticated: SELECT / admin: ALL
-- ------------------------------------------------------------
CREATE POLICY "Public read categories"
    ON products.categories FOR SELECT
    USING (true);

CREATE POLICY "Admin manages categories"
    ON products.categories FOR ALL
    USING (hr.current_level() = 2)
    WITH CHECK (hr.current_level() = 2);

-- ------------------------------------------------------------
-- products.products — anon + authenticated: SELECT / admin: ALL
-- ------------------------------------------------------------
CREATE POLICY "Public read products"
    ON products.products FOR SELECT
    USING (true);

CREATE POLICY "Admin manages products"
    ON products.products FOR ALL
    USING (hr.current_level() = 2)
    WITH CHECK (hr.current_level() = 2);

-- ------------------------------------------------------------
-- products.product_pictures — anon + authenticated: SELECT / admin: ALL
-- ------------------------------------------------------------
CREATE POLICY "Public read pictures"
    ON products.product_pictures FOR SELECT
    USING (true);

CREATE POLICY "Admin manages pictures"
    ON products.product_pictures FOR ALL
    USING (hr.current_level() = 2)
    WITH CHECK (hr.current_level() = 2);

-- ------------------------------------------------------------
-- clients.clients
--   anon      : INSERT (registration)
--   client    : SELECT own row
--   admin     : ALL
-- ------------------------------------------------------------
CREATE POLICY "Anon can register"
    ON clients.clients FOR INSERT
    WITH CHECK (auth.uid() IS NULL OR auth.uid() = auth_id);

CREATE POLICY "Client reads own profile"
    ON clients.clients FOR SELECT
    USING (auth_id = auth.uid());

CREATE POLICY "Admin manages clients"
    ON clients.clients FOR ALL
    USING (hr.current_level() = 2)
    WITH CHECK (hr.current_level() = 2);

-- ------------------------------------------------------------
-- clients.delivery_addresses
--   client : ALL on own addresses
--   admin  : SELECT
-- ------------------------------------------------------------
CREATE POLICY "Client manages own addresses"
    ON clients.delivery_addresses FOR ALL
    USING (client_id = clients.current_client_id())
    WITH CHECK (client_id = clients.current_client_id());

CREATE POLICY "Admin reads addresses"
    ON clients.delivery_addresses FOR SELECT
    USING (hr.current_level() = 2);

-- ------------------------------------------------------------
-- orders.orders
--   client      : INSERT + SELECT own orders
--   deliverer   : SELECT assigned orders + UPDATE status
--   admin       : ALL
-- ------------------------------------------------------------
CREATE POLICY "Client creates orders"
    ON orders.orders FOR INSERT
    WITH CHECK (client_id = clients.current_client_id());

CREATE POLICY "Client reads own orders"
    ON orders.orders FOR SELECT
    USING (client_id = clients.current_client_id());

CREATE POLICY "Deliverer reads assigned orders"
    ON orders.orders FOR SELECT
    USING (
        hr.is_employee()
        AND hr.current_level() = 1
        AND deliverer_id = hr.current_employee_id()
    );

CREATE POLICY "Deliverer updates assigned order status"
    ON orders.orders FOR UPDATE
    USING (
        hr.is_employee()
        AND hr.current_level() = 1
        AND deliverer_id = hr.current_employee_id()
    )
    WITH CHECK (status IN ('on_the_way', 'delivered', 'cancelled'));

CREATE POLICY "Admin manages orders"
    ON orders.orders FOR ALL
    USING (hr.current_level() = 2)
    WITH CHECK (hr.current_level() = 2);

-- ------------------------------------------------------------
-- orders.order_details
--   client    : INSERT + SELECT own order details
--   deliverer : SELECT details of assigned orders
--   admin     : ALL
-- ------------------------------------------------------------
CREATE POLICY "Client creates order details"
    ON orders.order_details FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM orders.orders o
            WHERE o.order_id  = order_id
              AND o.client_id = clients.current_client_id()
        )
    );

CREATE POLICY "Client reads own order details"
    ON orders.order_details FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM orders.orders o
            WHERE o.order_id  = order_id
              AND o.client_id = clients.current_client_id()
        )
    );

CREATE POLICY "Deliverer reads assigned order details"
    ON orders.order_details FOR SELECT
    USING (
        hr.is_employee()
        AND hr.current_level() = 1
        AND EXISTS (
            SELECT 1 FROM orders.orders o
            WHERE o.order_id     = order_id
              AND o.deliverer_id = hr.current_employee_id()
        )
    );

CREATE POLICY "Admin manages order details"
    ON orders.order_details FOR ALL
    USING (hr.current_level() = 2)
    WITH CHECK (hr.current_level() = 2);

-- ------------------------------------------------------------
-- hr.jobs — employees: SELECT / admin: ALL
-- ------------------------------------------------------------
CREATE POLICY "Employees read jobs"
    ON hr.jobs FOR SELECT
    USING (hr.is_employee());

CREATE POLICY "Admin manages jobs"
    ON hr.jobs FOR ALL
    USING (hr.current_level() = 2)
    WITH CHECK (hr.current_level() = 2);

-- ------------------------------------------------------------
-- hr.employees — employee: SELECT own row / admin: ALL
-- ------------------------------------------------------------
CREATE POLICY "Employee reads own profile"
    ON hr.employees FOR SELECT
    USING (auth_id = auth.uid());

CREATE POLICY "Admin manages employees"
    ON hr.employees FOR ALL
    USING (hr.current_level() = 2)
    WITH CHECK (hr.current_level() = 2);


-- ============================================================
-- 5. SEED — Default admin
-- ============================================================

-- Insert the admin job level
INSERT INTO hr.jobs (name, level)
VALUES ('Admin', 2);

-- Insert default admin employee
-- ⚠️  Change email, password and name on first login
-- ⚠️  password_hash is 'admin1234' — replace immediately
INSERT INTO hr.employees (
    job_id,
    name,
    phone,
    email,
    password_hash,
    status
)
VALUES (
    1,
    'Administrador',
    '0000000000',
    'admin@chucheritas.local',
    '$2b$12$placeholderHashChangeMe000000000000000000000000000000',
    'active'
);

-- ⚠️  After inserting the admin in Supabase Auth dashboard,
--     link their auth.users UUID with:
--
--     UPDATE hr.employees
--        SET auth_id = '<uuid-from-auth.users>'
--      WHERE email = 'admin@chucheritas.local';
