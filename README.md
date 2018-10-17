# Payments Microservice

## Introduction

This repository is the hub for a RESTful microservice that handles Payments for an eCommerce website. 
The website is being developed by NYU's DevOps and Agile Methodologies class (Fall 2018).

The Payments resource is responsible for processing all payment-related operations. These include operations such as a customer picking his/her payment method, payment authorization, printing/emailing receipts, etc.

## Prerequisite Installation using Vagrant

This service requires [VirtualBox](https://www.virtualbox.org/) and [VirtualBox](https://www.virtualbox.org/) to run. After installing the software, you can clone the repo and run the tests by using the following commands.

    git clone https://github.com/nyu-devops-payments/payments.git
    cd lab-flask-tdd
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

### Update an Existing Card
This endpoint will update a Card based the body that is posted.

    PUT /cards/{number}
    
#### Route Parameters

**number** (INTEGER) The card ID

#### HTTP Request Body Example

    {
        number: "12345",
        exp_month: 5,
        exp_year: 2020,
        cvc: "12345"
        address_zip: "12345",
        balance: 12.12
    }
  
#### HTTP Request Body Example

    {
        number: "12345",
        exp_month: 5,
        exp_year: 2020,
        cvc: "12345"
        address_zip: "12345",
        balance: 12.12
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
