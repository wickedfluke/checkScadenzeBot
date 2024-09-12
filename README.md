# Telegram Customer Management Bot

This is a Telegram bot that allows the admin to manage customers with product expiration dates. The bot enables the admin to add customers, remove them, renew expirations, send notifications, and much more. Customers can have multiple products and expiration dates and will automatically receive notifications three days before the expiration and on the day of expiration if not renewed.

## Features

- **Add Customer**: The admin can add customers with one or more products and their respective expiration dates.
- **List Customers**: The admin can view the complete list of customers and their products with expiration dates.
- **Remove Customer**: The admin can remove a customer from the list.
- **Renew Expiration**: The admin can extend a customer’s product expiration date by 30 days.
- **Send General Message**: The admin can send a message to all customers.
- **Automatic Notifications**: Customers will receive a notification 3 days before the product expiration and on the day of expiration.
- **Admin Only Access**: Only the admin can use management functions. Non-admin users can view their product expiration dates or be notified that they have no active subscriptions.
