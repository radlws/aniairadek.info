$(function() {

    $("input,textarea").jqBootstrapValidation({
        preventSubmit: true,
        submitError: function($form, event, errors) {
            // additional error messages or events
        },
        submitSuccess: function($form, event) {
            event.preventDefault(); // prevent default submit behaviour
            // get values from FORM
            var name = $("input#name").val();
            var email = $("input#email").val();
            var attending = $("select#attending").val();
            var no_guests = $("select#no_guests").val();
            // var phone = $("input#phone").val();
            var address = $("input#address").val();
            var food_message = $("input#food_message").val();
            // var message = $("textarea#message").val();
            
            //var firstName = name; // For Success/Failure Message
            //// Check for white space in name for Success/Fail message
            //if (firstName.indexOf(' ') >= 0) {
            //    firstName = name.split(' ').slice(0, -1).join(' ');
            //}

            var data_arr = {name: name, email: email, attending: attending, no_guests: no_guests, address: address, food_message: food_message};

            $.ajax({
                url: "/api/rsvp",
                type: "POST",
                data: JSON.stringify(data_arr),
                cache: false,
                contentType: 'application/json; charset=utf-8',
                dataType: 'json',
                success: function(response) {
                    // Success message

                    if (response['success']) {
                        $('#success').html("<div class='alert alert-success'>");
                        $('#success > .alert-success').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                            .append("</button>");
                        $('#success > .alert-success')
                            .append("<strong>Your RSVP has been sent. </strong>");
                        $('#success > .alert-success')
                            .append('</div>');
                    } else {

                        $('#success').html("<div class='alert alert-danger'>");
                        $('#success > .alert-danger').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                            .append("</button>");
                        $('#success > .alert-danger').append("<strong>" + response['msg'] + "</strong>");
                        $('#success > .alert-danger').append('</div>');
                    }

                    //clear all fields
                    $('#contactForm').trigger("reset");
                },
                error: function() {
                    // Fail message
                    $('#success').html("<div class='alert alert-danger'>");
                    $('#success > .alert-danger').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                        .append("</button>");
                    $('#success > .alert-danger').append("<strong>Sorry , it seems that my mail server is not responding. Please try again later!</strong>");
                    $('#success > .alert-danger').append('</div>');
                    //clear all fields
                    $('#contactForm').trigger("reset");
                }
            })
        },
        filter: function() {
            return $(this).is(":visible");
        }
    });

    $("a[data-toggle=\"tab\"]").click(function(e) {
        e.preventDefault();
        $(this).tab("show");
    });
});


/*When clicking on Full hide fail/success boxes */
$('#name').focus(function() {
    $('#success').html('');
});
