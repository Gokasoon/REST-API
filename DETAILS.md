# REST-API Application

This REST-API application is responsible for handling internet orders using Flask, PostgreSQL, and Redis. The application provides endpoints for managing products, creating orders, and processing payments.

## Features

- **Product Management**: 
  - View available products.
  - Check product details including name, type, description, image, height, weight, price, and stock status.

- **Order Management**:
  - Create new orders with multiple products.
  - View order details including total price, shipping price, payment status, and ordered products.
  - Update order information including shipping details and payment information.

- **Payment Processing**:
  - Integrate with an external payment service to process credit card payments.
  - Store transaction details and update order status upon successful payment.

- **Web Interface**:
  - User-friendly web interface for viewing products, creating orders, and checking order status.
  - Templates for product listing, order form, order information, and order checking.