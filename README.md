# Smartech Home Assignment

## Description

This project aims to create a RESTful API with CRUD functions using Python

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Metrics](#metrics)

## Installation

```bash
 poetry install
```

## Usage

1. Run app.py 
```bash
 poetry run python app.py
```

2. Edit the database using curl methods. Examples:
    Create a new user:
    ```bash
    curl -X POST "http://127.0.0.1:5000/users" \
        -u admin:admin \
        -H "Content-Type: application/json" \
        -d '{"username": "newuser", "password": "newpassword"}'
    ```

    Get all users:
    ```bash
    curl -X GET "http://127.0.0.1:5000/users" \
    -u admin:admin
    ```
    
    Update a user:
    ```bash
    curl -X PUT "http://127.0.0.1:5000/users/1" \
    -u admin:admin \
    -H "Content-Type: application/json" \
    -d '{"username": "updateduser", "password": "newpassword123"}'
    ```
    Delete a user:
    ```bash
    curl -X DELETE "http://127.0.0.1:5000/users/1" \
    -u admin:admin
    ```

## Testing

```bash
 poetry run pytest
```

## Metrics

To see usage metrics:
```bash
curl -X GET "http://127.0.0.1:5000/metrics"
```