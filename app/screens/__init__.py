"""One Component per slot. State, actions, and view live together."""

from app.screens.account import Account
from app.screens.bag import Cart
from app.screens.checkout import Checkout, Confirm, empty_checkout
from app.screens.home import Home
from app.screens.orders import Order, Orders
from app.screens.product import Product
from app.screens.shop import Shop
from app.screens.wish import Wish

__all__ = [
    "Account",
    "Cart",
    "Checkout",
    "Confirm",
    "Home",
    "Order",
    "Orders",
    "Product",
    "Shop",
    "Wish",
    "empty_checkout",
]
