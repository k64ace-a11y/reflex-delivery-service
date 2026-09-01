from pydantic import BaseModel


class DeliveryRequest(BaseModel):
    customer_name: str
    customer_phone: str
    address: str
    item_description: str


class AssignRequest(BaseModel):
    rider: str


class StatusRequest(BaseModel):
    status: str