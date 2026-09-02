// Your FastAPI backend on Render
const API_BASE_URL = "https://reflex-delivery-service.onrender.com";


// ===============================
// CREATE DELIVERY
// ===============================

document
    .getElementById("deliveryForm")
    .addEventListener("submit", async function (event) {

        event.preventDefault();

        const delivery = {
            customer_name: document.getElementById("customer_name").value,
            customer_phone: document.getElementById("customer_phone").value,
            address: document.getElementById("address").value,
            item_description: document.getElementById("item_description").value
        };

        try {
            const response = await fetch(`${API_BASE_URL}/deliveries`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(delivery)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Failed to create delivery");
            }

            document.getElementById("deliveryResult").innerHTML = `
                <div class="delivery">
                    <h3>Delivery Created Successfully</h3>
                    <p><strong>Delivery ID:</strong> ${data.id}</p>
                    <p><strong>Order Code:</strong> ${data.order_code}</p>
                    <p><strong>Status:</strong> ${data.status}</p>
                </div>
            `;

            document.getElementById("deliveryForm").reset();

            loadOpenDeliveries();

        } catch (error) {
            document.getElementById("deliveryResult").innerHTML = `
                <p>Error: ${error.message}</p>
            `;
        }
    });


// ===============================
// LOAD OPEN DELIVERIES
// ===============================

async function loadOpenDeliveries() {

    const container = document.getElementById("openDeliveries");

    container.innerHTML = "Loading...";

    try {

        const response = await fetch(`${API_BASE_URL}/deliveries/open`);

        const deliveries = await response.json();

        if (!response.ok) {
            throw new Error("Could not load deliveries");
        }

        if (deliveries.length === 0) {
            container.innerHTML = "<p>No open deliveries.</p>";
            return;
        }

        container.innerHTML = "";

        deliveries.forEach(delivery => {

            container.innerHTML += `
                <div class="delivery">

                    <h3>Delivery #${delivery.id}</h3>

                    <p>
                        <strong>Customer:</strong>
                        ${delivery.customer_name}
                    </p>

                    <p>
                        <strong>Phone:</strong>
                        ${delivery.customer_phone}
                    </p>

                    <p>
                        <strong>Address:</strong>
                        ${delivery.address}
                    </p>

                    <p>
                        <strong>Item:</strong>
                        ${delivery.item_description}
                    </p>

                    <p class="status">
                        Status: ${delivery.status}
                    </p>

                    <input
                        type="text"
                        id="rider-${delivery.id}"
                        placeholder="Rider name"
                    >

                    <button onclick="assignRider(${delivery.id})">
                        Assign Rider
                    </button>

                </div>
            `;
        });

    } catch (error) {

        container.innerHTML = `
            <p>Error loading deliveries: ${error.message}</p>
        `;

    }
}


// ===============================
// ASSIGN RIDER
// ===============================

async function assignRider(deliveryId) {

    const rider = document.getElementById(`rider-${deliveryId}`).value;

    if (!rider) {
        alert("Please enter the rider name.");
        return;
    }

    try {

        const response = await fetch(
            `${API_BASE_URL}/deliveries/${deliveryId}/assign`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    rider: rider
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Assignment failed");
        }

        alert("Rider assigned successfully!");

        loadOpenDeliveries();

    } catch (error) {

        alert(`Error: ${error.message}`);

    }
}


// ===============================
// LOAD RIDER DELIVERIES
// ===============================

async function loadRiderDeliveries() {

    const rider = document.getElementById("riderName").value;

    if (!rider) {
        alert("Please enter your rider name.");
        return;
    }

    const container = document.getElementById("riderDeliveries");

    container.innerHTML = "Loading...";

    try {

        const response = await fetch(
            `${API_BASE_URL}/riders/${encodeURIComponent(rider)}/deliveries`
        );

        const deliveries = await response.json();

        if (!response.ok) {
            throw new Error("Could not load rider deliveries");
        }

        if (deliveries.length === 0) {
            container.innerHTML = "<p>No deliveries assigned to you.</p>";
            return;
        }

        container.innerHTML = "";

        deliveries.forEach(delivery => {

            container.innerHTML += `
                <div class="delivery">

                    <h3>Order: ${delivery.order_code}</h3>

                    <p>
                        <strong>Customer:</strong>
                        ${delivery.customer_name}
                    </p>

                    <p>
                        <strong>Address:</strong>
                        ${delivery.address}
                    </p>

                    <p class="status">
                        Status: ${delivery.status}
                    </p>

                    <button onclick="updateStatus(${delivery.id}, 'Picked Up')">
                        Picked Up
                    </button>

                    <button onclick="updateStatus(${delivery.id}, 'Delivered')">
                        Delivered
                    </button>

                </div>
            `;
        });

    } catch (error) {

        container.innerHTML = `
            <p>Error: ${error.message}</p>
        `;

    }
}


// ===============================
// UPDATE DELIVERY STATUS
// ===============================

async function updateStatus(deliveryId, status) {

    try {

        const response = await fetch(
            `${API_BASE_URL}/deliveries/${deliveryId}/status`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: status
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Status update failed");
        }

        alert(`Delivery marked as ${status}.`);

        loadRiderDeliveries();

    } catch (error) {

        alert(`Error: ${error.message}`);

    }
}