# Brief Description of the Repository

This repository is the hub for a RESTful microservice that handles Payments for an eCommerce website. 
The website is being developed by NYU's DevOps and Agile Methodologies class (Fall 2018).

The Payments resource is responsible for processing all payment-related operations. These include operations such as a customer picking his/her payment method, payment authorization, printing/emailing receipts, etc.

## Prerequisite Installation using Vagrant

This service requires [VirtualBox](https://www.virtualbox.org/) and [VirtualBox](https://www.virtualbox.org/) to run. After installing the software, you can clone the repo and run the tests by using the following commands.

    git clone https://github.com/nyu-devops/lab-flask-tdd.git
    cd lab-flask-tdd
    vagrant up
    vagrant ssh
    cd /vagrant
    nosetests


## API structure

