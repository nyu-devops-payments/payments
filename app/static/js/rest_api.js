$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#payment_id").val(res.id);
        $("#payment_customer_id").val(res.customer_id);
        $("#payment_order_id").val(res.order_id);
        $("#payment_payment_method_type").val("HEYYY");

        if (res.payment_method_type == "PaymentMethodType.DEBIT") {
            $("#payment_payment_method_type").val("DEBIT");
        }

        else if (res.payment_method_type == "PaymentMethodType.CREDIT") {
            $("#payment_payment_method_type").val("CREDIT");
        }

        else if (res.payment_method_type == "PaymentMethodType.PAYPAL") {
            $("#payment_payment_method_type").val("PAYPAL");
        }

        if (res.payment_status == "PaymentStatus.PAID") {
            $("#payment_payment_status").val("PAID");
        }

        else if (res.payment_status == "PaymentStatus.PROCESSING") {
            $("#payment_payment_status").val("PROCESSING");
        }

        else if (res.payment_status == "PaymentStatus.UNPAID") {
            $("#payment_payment_status").val("UNPAID");
        }

        // $("#payment_payment_status").val(res.payment_status);
        if (res.default_payment_type == true) {
            $("#payment_default_payment_type").val("true");
        } else {
            $("#payment_default_payment_type").val("false");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#payment_id").val("");
        $("#payment_customer_id").val("");
        $("#payment_order_id").val("");
        $("#payment_payment_method_type").val("");
        $("#payment_payment_status").val("");
        $("#payment_default_payment_type").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Payment
    // ****************************************

    $("#create-btn").click(function () {

        var id = $("#payment_id").val();
        var customer_id = $("#payment_customer_id").val();
        var order_id = $("#payment_order_id").val();
        var payment_method_type = $("#payment_payment_method_type").val();
        var payment_status = $("#payment_payment_status").val();
        var default_payment_type = $("#payment_default_payment_type").val() == "false";

        var data = {
            "id": id,
            "customer_id": customer_id,
            "order_id": order_id,
            "payment_method_type": "DEBIT",
            "payment_status": payment_status,
            "default_payment_type": default_payment_type
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/payments",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success - Payment Added!")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Payment
    // ****************************************

    $("#update-btn").click(function () {

        var id = $("#payment_id").val();
        var customer_id = $("#payment_customer_id").val();
        var order_id = $("#payment_order_id").val();
        var payment_method_type = $("#payment_payment_method_type").val();
        var payment_status = $("#payment_payment_status").val();
        var default_payment_type = $("#payment_default_payment_type").val() == "false";

        var data = {
            "id": id,
            "customer_id": customer_id,
            "order_id": order_id,
            "payment_method_type": payment_method_type,
            "payment_status": payment_status,
            "default_payment_type": default_payment_type
        };

        var ajax = $.ajax({
            type: "PUT",
            url: "/payments/" + id,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Payment
    // ****************************************

    $("#retrieve-btn").click(function () {

        var id = $("#payment_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/payments/" + id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success!!")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Payment
    // ****************************************

    $("#delete-btn").click(function () {

        var id = $("#payment_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/payments/" + id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Payment with ID [" + res.id + "] has been Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#payment_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Payment
    // ****************************************

    $("#search-btn").click(function () {

        var id = $("#payment_id").val();
        var customer_id = $("#payment_customer_id").val();
        var order_id = $("#payment_order_id").val();
        var payment_method_type = $("#payment_payment_method_type").val();
        var payment_status = $("#payment_payment_status").val();
        var default_payment_type = $("#payment_default_payment_type").val() == "false";

        var queryString = "";


        if (id) {
            queryString += 'id=' + id;
        }
        if (customer_id) {
            queryString += 'customer_id=' + customer_id;
        }
        if (order_id) {
            queryString += 'order_id' + order_id;
        }
        if (payment_method_type) {
            queryString += 'payment_method_type' + payment_method_type;
        }
        if (payment_status) {
            queryString += 'payment_status' + payment_status;
        }
        if (default_payment_type) {
            if (queryString.length > 0) {
                queryString += '&default_payment_type=' + default_payment_type;
            } else {
                queryString += 'default_payment_type=' + default_payment_type;
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/payments?" + queryString,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function (res) {
            //alert(res.toSource())
            for(var i = 0; i < res.length; i++) {

            var html = '';
            html += '<table class="table-striped pad-10">';
            html += '<tr>';
            html += '<th style="width:10%">ID</th>';
            html += '<th style="width:40%">Customer ID</th>';
            html += '<th style="width:40%">Order ID</th>';
            html += '<th style="width:10%">Payment Method Type</th>';
            html += '<th style="width:10%">Payment Status</th>';
            html += '<th style="width:10%">Default Payment Type</th>';
            html += '</tr>';

            for (var i = 0; i < res.length; i++) {
                payment = res[i];
                html += "<tr><td>" + payment.id + "</td><td>" + payment.customer_id + "</td><td>" + payment.order_id + "</td><td>" + payment.payment_method_type + "</td><td>" + payment.payment_status + "</td><td>" + payment.default_payment_type + "</td></tr>";
            }

            html += '</table>';

            $("#search_results").empty();
            $("#search_results").append(html);

            flash_message("Success");
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message);
        });

    });

});