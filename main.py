from fastapi import FastAPI, HTTPException

from database import create_database, get_connection
from models import DeliveryRequest, AssignRequest, StatusRequest


app = FastAPI(
    title="Reflex Delivery Service",
    description="Simple delivery management service for Kenyan retailers",
    version="1.0.0"
)


# ==========================================
# STARTUP
# ==========================================

@app.on_event("startup")
def startup():
    create_database()


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():
    return {
        "service": "Reflex",
        "message": "Delivery service is running"
    }


# ==========================================
# CREATE DELIVERY
# Retailer function
# ==========================================

@app.post("/deliveries")
def create_delivery(delivery: DeliveryRequest):

    connection = get_connection()
    cursor = connection.cursor()

    # Get number of existing deliveries
    cursor.execute("SELECT COUNT(*) FROM deliveries")
    count = cursor.fetchone()[0]

    # Create order code
    order_code = f"REFLEX-{count + 1:04d}"

    cursor.execute("""
        INSERT INTO deliveries (
            customer_name,
            customer_phone,
            address,
            item_description,
            status,
            order_code
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        delivery.customer_name,
        delivery.customer_phone,
        delivery.address,
        delivery.item_description,
        "Open",
        order_code
    ))

    connection.commit()

    delivery_id = cursor.lastrowid

    connection.close()

    return {
        "message": "Delivery request created",
        "delivery_id": delivery_id,
        "order_code": order_code,
        "status": "Open"
    }


# ==========================================
# VIEW OPEN DELIVERIES
# Dispatcher function
# ==========================================

@app.get("/deliveries/open")
def get_open_deliveries():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM deliveries
        WHERE status = 'Open'
        ORDER BY id DESC
    """)

    deliveries = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return {
        "count": len(deliveries),
        "deliveries": deliveries
    }


# ==========================================
# ASSIGN RIDER
# Dispatcher function
# ==========================================

@app.put("/deliveries/{delivery_id}/assign")
def assign_rider(
    delivery_id: int,
    assignment: AssignRequest
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM deliveries WHERE id = ?",
        (delivery_id,)
    )

    delivery = cursor.fetchone()

    if not delivery:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Delivery not found"
        )

    cursor.execute("""
        UPDATE deliveries
        SET rider = ?, status = 'Assigned'
        WHERE id = ?
    """, (
        assignment.rider,
        delivery_id
    ))

    connection.commit()
    connection.close()

    return {
        "message": "Rider assigned successfully",
        "delivery_id": delivery_id,
        "rider": assignment.rider,
        "status": "Assigned"
    }


# ==========================================
# VIEW RIDER DELIVERIES
# Rider function
# ==========================================

@app.get("/riders/{rider}/deliveries")
def get_rider_deliveries(rider: str):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM deliveries
        WHERE rider = ?
        ORDER BY id DESC
    """, (rider,))

    deliveries = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return {
        "rider": rider,
        "deliveries": deliveries
    }


# ==========================================
# UPDATE DELIVERY STATUS
# Rider function
# ==========================================

@app.put("/deliveries/{delivery_id}/status")
def update_status(
    delivery_id: int,
    status_request: StatusRequest
):

    allowed_statuses = [
        "Assigned",
        "Picked Up",
        "Delivered"
    ]

    if status_request.status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail="Invalid status. Use Assigned, Picked Up or Delivered."
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM deliveries WHERE id = ?",
        (delivery_id,)
    )

    delivery = cursor.fetchone()

    if not delivery:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Delivery not found"
        )

    cursor.execute("""
        UPDATE deliveries
        SET status = ?
        WHERE id = ?
    """, (
        status_request.status,
        delivery_id
    ))

    connection.commit()
    connection.close()

    return {
        "message": "Delivery status updated",
        "delivery_id": delivery_id,
        "status": status_request.status
    }


# ==========================================
# VIEW ONE DELIVERY
# Retailer tracking function
# ==========================================

@app.get("/deliveries/{delivery_id}")
def get_delivery(delivery_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM deliveries WHERE id = ?",
        (delivery_id,)
    )

    delivery = cursor.fetchone()

    connection.close()

    if not delivery:

        raise HTTPException(
            status_code=404,
            detail="Delivery not found"
        )

    return dict(delivery)


# ==========================================
# SYNC
# Get latest delivery information
# ==========================================

@app.get("/sync")
def sync_deliveries():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM deliveries
        ORDER BY id DESC
    """)

    deliveries = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return {
        "message": "Sync successful",
        "deliveries": deliveries
    }


# ==========================================
# SCAN / CONFIRM ORDER
# ==========================================

@app.post("/scan/{order_code}")
def scan_order(order_code: str):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM deliveries
        WHERE order_code = ?
    """, (order_code,))

    delivery = cursor.fetchone()

    connection.close()

    if not delivery:

        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return {
        "message": "Order confirmed successfully",
        "order": dict(delivery)
    }