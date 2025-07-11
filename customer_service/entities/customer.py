"""Customer entity module."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class Address(BaseModel):
    """
    Represents a customer's address.
    """

    street: str
    city: str
    state: str
    zip: str
    model_config = ConfigDict(from_attributes=True)


class Product(BaseModel):
    """
    Represents a product in a customer's purchase history.
    """

    product_id: str
    name: str
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class Purchase(BaseModel):
    """
    Represents a customer's purchase.
    """

    date: str
    items: List[Product]
    total_amount: float
    model_config = ConfigDict(from_attributes=True)


class CommunicationPreferences(BaseModel):
    """
    Represents a customer's communication preferences.
    """

    email: bool = True
    sms: bool = True
    push_notifications: bool = True
    model_config = ConfigDict(from_attributes=True)


class Customer(BaseModel):
    """
    Represents a customer.
    """

    account_number: str
    customer_id: str
    customer_first_name: str
    customer_last_name: str
    email: str
    phone_number: str
    customer_start_date: str
    years_as_customer: int
    billing_address: Address
    purchase_history: List[Purchase]
    loyalty_points: int
    preferred_store: str
    communication_preferences: CommunicationPreferences
    scheduled_appointments: Dict = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)

    def to_json(self) -> str:
        """
        Converts the Customer object to a JSON string.

        Returns:
            A JSON string representing the Customer object.
        """
        return self.model_dump_json(indent=4)

    @staticmethod
    def get_customer(current_customer_id: str, account_number: str) -> Optional["Customer"]:
        """
        Retrieves a customer based on their ID.

        Args:
            current_customer_id: The ID of the customer to retrieve.
            account_number: The account number of the customer.

        Returns:
            The Customer object if found, None otherwise.
        """
        # In a real application, this would involve a database lookup.
        # For this example, we'll just return a dummy customer.
        return Customer(
            customer_id=current_customer_id,
            account_number=account_number,
            customer_first_name="John",
            customer_last_name="Johnson",
            email="John.johnson@example.com",
            phone_number="+1-702-555-1212",
            customer_start_date="2022-06-10",
            years_as_customer=2,
            billing_address=Address(
                street="123 Main St", city="Anytown", state="CA", zip="12345"
            ),
            purchase_history=[  # Example purchase history
                Purchase(
                    date="2023-03-05",
                    items=[
                        Product(
                            product_id="vm-n1-111",
                            name="N1 Standard Instance (2 vCPU)",
                            quantity=1,
                        ),
                        Product(
                            product_id="disk-222",
                            name="Persistent Disk 100GB SSD",
                            quantity=1,
                        ),
                    ],
                    total_amount=125.40,
                ),
                Purchase(
                    date="2023-07-12",
                    items=[
                        Product(
                            product_id="vm-c2-333",
                            name="C2 High-CPU Instance (4 vCPU)",
                            quantity=2,
                        ),
                        Product(
                            product_id="ip-444",
                            name="Static IP Address",
                            quantity=2,
                        ),
                    ],
                    total_amount=245.80,
                ),
                Purchase(
                    date="2024-01-20",
                    items=[
                        Product(
                            product_id="vm-e2-555",
                            name="E2 Standard Instance (8 vCPU)",
                            quantity=1,
                        ),
                        Product(
                            product_id="snapshot-666",
                            name="Disk Snapshot Service",
                            quantity=1,
                        ),
                    ],
                    total_amount=320.15,
                ),
            ],
            loyalty_points=133,
            communication_preferences=CommunicationPreferences(
                email=True, sms=False, push_notifications=True
            ),
            scheduled_appointments={},
        )
