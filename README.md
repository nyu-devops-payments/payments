# Payments Microservice

[![Build Status](https://travis-ci.org/nyu-devops-payments/payments.svg?branch=master)](https://travis-ci.org/nyu-devops-payments/payments)
[![Codecov](https://codecov.io/gh/nyu-devops-payments/payments/branch/master/graph/badge.svg)](https://codecov.io/gh/nyu-devops-payments/payments/branch/master/graph/badge.svg)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Introduction

This repository is the hub for a RESTful microservice that handles Payments for an eCommerce website. 
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

### List All Cards
This endpoint returns all of the Cards.

    GET /cards

### Retrieve a Single Card
This endpoint will return a Card based on its number.

    GET /cards/{number}

#### Route Parameters

**number** (INTEGER) The card ID

### Add a New Card
This endpoint will create a Payment source based on the Card Info in the body that is posted.

    POST /cards

#### HTTP Request Body Example

    {
        "number": "4242424242424242",
        "exp_month": 5,
        "exp_year": 2020,
        "cvc": "123",
        "address_zip": "12345",
        "name": "Dennis John",
        "balance": 105.00
    }
   
### Update an Existing Card
This endpoint will update a Card based the body that is posted.

    PUT /cards/{number}
    
#### Route Parameters

**number** (INTEGER) The card ID

#### HTTP Request Body Example

    {
        "number": "4242424242424242",
        "exp_month": 5,
        "exp_year": 2020,
        "cvc": "123",
        "address_zip": "12345",
        "name": "Dennis John",
        "balance": 105.00
    }

### Delete a Card
This endpoint will delete a Card based the id specified in the path.

    DELETE /cards/{number}

#### Route Parameters

**number** (INTEGER) The card ID

### Perform Action - Charge a Card
This endpoint will charge a purchase against a card.

    PUT /cards/{number}/{amount}

#### Route Parameters

**number** (INTEGER) The card ID

**amount** (FLOAT) The amount to charge


#### Test Code Coverage
A code coverage of 93% has been achieved for the Payments API. Testing all endpoints + mock tests for bad requests.
