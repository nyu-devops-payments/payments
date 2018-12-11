# Payments Microservice

[![Build Status](https://travis-ci.org/nyu-devops-payments/payments.svg?branch=master)](https://travis-ci.org/nyu-devops-payments/payments)
[![Codecov](https://codecov.io/gh/nyu-devops-payments/payments/branch/master/graph/badge.svg)](https://codecov.io/gh/nyu-devops-payments/payments/branch/master/graph/badge.svg)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Introduction

This repository is the hub for a RESTful Micro-Service that handles Payments for an eCommerce website.
The website is being developed by NYU's DevOps and Agile Methodologies class (Fall 2018).

The Payments resource is responsible for processing all payment-related operations. These include operations such as a customer picking his/her payment method, payment authorization, printing/emailing receipts, etc.

## Prerequisite Installation using Vagrant

This service requires [VirtualBox](https://www.virtualbox.org/) and [VirtualBox](https://www.virtualbox.org/) to run. After installing the software, you can clone the repo and run the tests by using the following commands.

    git clone https://github.com/nyu-devops-payments/payments.git
    cd payments
    vagrant up
    vagrant ssh
    cd /vagrant
    nosetests


## API Structure

Below are the available endpoints of this microservice.

### List All Payments
This endpoint returns all of the Cards.

    GET /payments

### Retrieve a Single Card
This endpoint will return a Card based on its number.

    GET /payments/{number}

#### Route Parameters

**id** (INTEGER) The Payment ID

### Add a New Payment
This endpoint will create a Payment source based on the Payment Info in the body that is posted.

    POST /payments

#### HTTP Request Body Example
    {
        "customer_id": 12302,
        "order_id": 11150,
        "payment_method_type": "CREDIT",
        "payment_status": "PAID"
        "default_payment_type": False,
    }


### Update an Existing Payment
This endpoint will update a Card based the body that is posted.

    PUT /payments/{number}

#### Route Parameters

**number** (INTEGER) The payment resource ID

#### HTTP Request Body Example

    {
      "customer_id": 12310,
      "order_id": 13151,
      "payment_method_type": "CREDIT",
      "payment_status": "PAID"
      "default_payment_type": False,
    }

### Delete a Payment 
This endpoint will delete a Card based the id specified in the path.

    DELETE /payments/{id}

#### Route Parameters

**number** (INTEGER) The payment ID


### Perform Action - Set a Payment as Default
This endpoint will set a Payment as default for a customer. If the customer already has a default, it will be replaced.

    PUT /payments/{id}/default

#### Route Parameters

**id** (INTEGER) The Payment ID


#### Test Code Coverage
A code coverage of 97% has been achieved for the Payments API. Testing all endpoints + mock tests for bad requests.
