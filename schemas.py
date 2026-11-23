REQUIRED_FIELDS = {
    "olist_customers_dataset.csv": [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix"
    ],

    "olist_geolocation_dataset.csv": [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng"
    ],

    "olist_orders_dataset.csv": [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp"
    ],

    "olist_order_items_dataset.csv": [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "price"
    ],

    "olist_order_payments_dataset.csv": [
        "order_id",
        "payment_sequential",
        "payment_type",
        "payment_value"
    ],

    "olist_order_reviews_dataset.csv": [
        "review_id",
        "order_id",
        "review_score"
    ],

    "olist_products_dataset.csv": [
        "product_id",
        "product_category_name"
    ],

    "olist_sellers_dataset.csv": [
        "seller_id",
        "seller_zip_code_prefix"
    ],
    
    "product_category_name_translation.csv": [
        "product_category_name",
        "product_category_name_english"
    ]
}

# Fields that must contain numeric values
NUMERIC_FIELDS = {
    "price",
    "freight_value",
    "payment_value",
    "payment_sequential",
    "payment_installments",
    "review_score",
    "order_item_id",
    "geolocation_lat",
    "geolocation_lng",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
}

# Fields that must contain valid dates
DATE_FIELDS = {
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
    "shipping_limit_date",
    "review_creation_date",
    "review_answer_timestamp"
}

# Allowed order statuses
ALLOWED_ORDER_STATUS = {
    "created",
    "approved",
    "invoiced",
    "processing",
    "shipped",
    "delivered",
    "unavailable",
    "canceled"
}

# Fields containing ZIP prefixes
ZIP_FIELDS = {
    "customer_zip_code_prefix",
    "seller_zip_code_prefix",
    "geolocation_zip_code_prefix"
}

# Maximum allowed rejected-row percentage
MAX_REJECTION_PERCENTAGE = 20
