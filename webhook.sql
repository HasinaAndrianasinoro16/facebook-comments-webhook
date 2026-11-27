-- Table parent
CREATE TABLE fb_webhook_feed (
    id_event          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    object_type       VARCHAR2(20),      -- "object" (page)
    entry_id          VARCHAR2(30),      -- id de la page
    descriptions      CLOB,
    entry_time        NUMBER(12),        -- epoch (secondes)
    entry_time_dt     TIMESTAMP,         -- epoch converti (UTC)
    field_name        VARCHAR2(20),      -- "field" (feed)
    from_id           VARCHAR2(30),
    from_name         VARCHAR2(100),
    item              VARCHAR2(20),      -- comment
    verb              VARCHAR2(20),      -- add / edited / remove
    messages          VARCHAR2(4000),
    comment_id        VARCHAR2(60),
    parent_id         VARCHAR2(60),
    post_id           VARCHAR2(60),
    created_time      NUMBER(12),        -- epoch (secondes)
    created_time_dt   TIMESTAMP,         -- epoch converti (UTC)
    post_status_type  VARCHAR2(30),
    post_is_published NUMBER(1),
    post_updated_time TIMESTAMP,
    post_permalink    VARCHAR2(500),
    promotion_status  VARCHAR2(20)
);

CREATE TABLE fb_com_manager (
    id_com NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_event NUMBER NOT NULL,
    status_feed  VARCHAR2(200),
    reponse VARCHAR(200),
    CONSTRAINT fk_com_event FOREIGN KEY (id_event)
        REFERENCES fb_webhook_feed (id_event)
);

CREATE TABLE fb_llm (
    id_llm NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_event NUMBER NOT NULL,
    libelle_sentiment VARCHAR2(500),
    sentiment NUMBER,
    libelle_categorie VARCHAR2(500),
    categorie NUMBER,
    CONSTRAINT fk_llm_event FOREIGN KEY (id_event)
        REFERENCES fb_webhook_feed (id_event)
);

CREATE INDEX idx_com_event ON fb_com_manager (id_event);
CREATE INDEX idx_llm_event ON fb_llm (id_event);