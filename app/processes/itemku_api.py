import os
import requests

from datetime import datetime

import base64
import hmac
import hashlib


import json



def base64_url_encode(data):
    """Encodes data using base64 URL encoding without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def generate_jwt_token(nonce, payload):
    """Generates a JWT token using HMAC SHA256."""
    # Create the header
    header = {
        "X-Api-Key": os.environ["ITEMKU_API_KEY"],
        "Nonce": nonce,
        "alg": "HS256",
    }

    # Base64 URL encode the header and payload
    encoded_header = base64_url_encode(json.dumps(header).encode("utf-8"))
    encoded_payload = base64_url_encode(json.dumps(payload).encode("utf-8"))

    # Create the unsigned token
    unsigned_token = f"{encoded_header}.{encoded_payload}"

    # Generate the HMAC SHA256 signature
    signature = hmac.new(
        os.environ["ITEMKU_SECRET_KEY"].encode("utf-8"),
        unsigned_token.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    encoded_signature = base64_url_encode(signature)

    # Combine to form the final JWT
    return f"{unsigned_token}.{encoded_signature}"


class ItemkuAPI:
    def __init__(
        self,
    ) -> None:
        pass

    def valid_price(self, price: int) -> int:
        return int(round(float(price) / 10, 0) * 10)

    def get_product_details(
        self,
        product_id: int,
    ):
        """
        Get product details from Itemku API using product list endpoint.

        Endpoint: POST https://tokoku-gateway.itemku.com/api/product/list

        Uses the product list API with id filter to get a single product's details.

        Returns:
            dict: Product details including current price
            Example response:
            {
                "success": true,
                "data": {
                    "data": [{
                        "id": 123456,
                        "name": "Product Name",
                        "price": 10000,
                        "stock": 50,
                        ...
                    }]
                }
            }
        """
        print(f"Call api get product details for product_id: {product_id}")
        nonce = str(int(datetime.now().timestamp()))

        payload = {
            "id": product_id,
            "page": 1
        }

        token = generate_jwt_token(
            nonce=nonce,
            payload=payload,
        )

        header = {
            "X-Api-Key": os.environ["ITEMKU_API_KEY"],
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Nonce": nonce,
        }

        res = requests.post(
            url="https://tokoku-gateway.itemku.com/api/product/list",
            headers=header,
            json=payload,
        )
        res.raise_for_status()

        return res.json()

    def update_price(
        self,
        product_id: int,
        new_price: int,
    ):
        print("Call api update price")
        nonce = str(int(datetime.now().timestamp()))

        payload = {
            "product_id": product_id,
            "new_price": new_price,
        }

        token = generate_jwt_token(
            nonce=nonce,
            payload=payload,
        )

        header = {
            "X-Api-Key": os.environ["ITEMKU_API_KEY"],
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Nonce": nonce,
        }

        res = requests.post(
            url="https://tokoku-gateway.itemku.com/api/product/price/update",
            headers=header,
            json=payload,
        )
        res.raise_for_status()

        return res.json()

    def update_stock(
        self,
        product_id: int,
        new_stock: int,
    ):
        """
        Update product stock using Itemku API.

        Endpoint: POST https://tokoku-gateway.itemku.com/api/product/stock/update

        Args:
            product_id: Product ID to update
            new_stock: New stock value (max 99999999)

        Note: Cannot update stock for auto delivery products
        """
        print(f"Call api update stock for product_id: {product_id}, new_stock: {new_stock}")
        nonce = str(int(datetime.now().timestamp()))

        payload = {
            "product_id": product_id,
            "new_stock": new_stock,
        }

        token = generate_jwt_token(
            nonce=nonce,
            payload=payload,
        )

        header = {
            "X-Api-Key": os.environ["ITEMKU_API_KEY"],
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Nonce": nonce,
        }

        res = requests.post(
            url="https://tokoku-gateway.itemku.com/api/product/stock/update",
            headers=header,
            json=payload,
        )
        res.raise_for_status()

        return res.json()


itemku_api = ItemkuAPI()
