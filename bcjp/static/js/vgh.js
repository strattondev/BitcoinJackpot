function postJobX() {
    $("#errorPanel").remove();
    $(".has-error").removeClass("has-error");

    var company;
    var error = false;
    var htmlBaseDanger = '<div class="alert alert-danger" id="errorPanel"><ul>';
    var htmlBaseSuccess = '<div class="alert alert-success" id="errorPanel"><ul>';
    var htmlBaseEnd = '</ul></div>';
    var errorArr = [];

    $("#groupCompanyExistingId").removeClass("has-error");
    $("#groupCompanyName").removeClass("has-error");
    $("#groupCompanyHomepage").removeClass("has-error");
    $("#groupTitle").removeClass("has-error");
    $("#groupDescription").removeClass("has-error");
    $("#groupApplicationInfo").removeClass("has-error");
    $("#groupEmail").removeClass("has-error");

    if ($("#existingCompany").hasClass("active")) {
        if ($("#companyExistingId").val() == null) {
            $("#groupCompanyExistingId").addClass("has-error");
            error = true;
            errorArr.push("<li>Please select a company or add a new company</li>")
        }

        company = $("#formExistingCompany").serialize();
    } else {
        if ($("#companyName").val().search(/\S/) != 0) {
            $("#groupCompanyName").addClass("has-error");
            error = true;
            errorArr.push("<li>Please enter a company name</li>")
        }

        if ($("#companyHomepage").val().search(/\S/) != 0) {
            $("#groupCompanyHomepage").addClass("has-error");
            error = true;
            errorArr.push("<li>Please enter a company homepage</li>")
        }

        company = $("#formNewCompany").serialize();
    }

    if ($("#title").val().search(/\S/) != 0) {
        $("#groupTitle").addClass("has-error");
        error = true;
        errorArr.push("<li>Please enter a job title</li>")
    }

    if ($("#description").val().search(/\S/) != 0) {
        $("#groupDescription").addClass("has-error");
        error = true;
        errorArr.push("<li>Please enter a job description</li>")
    }

    if ($("#applicationInfo").val().search(/\S/) != 0) {
        $("#groupApplicationInfo").addClass("has-error");
        error = true;
        errorArr.push("<li>Please enter job application info</li>")
    }

    var re = /^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;

    if ($("#email").val().search(/\S/) != 0 || !re.test($("#email").val())) {
        $("#groupEmail").addClass("has-error");
        error = true;
        errorArr.push("<li>Please enter a valid email address</li>")
    }

    if (error) {
        var html = htmlBaseDanger;

        for (var i = 0; i < errorArr.length; ++i) {
            html += errorArr[i];
        }

        html += htmlBaseEnd;

        $("#companyChoiceStart").prepend(html);
        $(window).scrollTop(0);
        return;
    }

    var formData = $("#formJob").serialize() + "&" + company;

    var handler = StripeCheckout.configure({
                key: 'pk_test_UMi9di6mRXqjM66nHnDY4TTx',
                image: '/img/documentation/checkout/marketplace.png',
                token: function(token) {
                    $.post("/post", formData + "&token=" + token.id, function(data) {
                        var html;
                        var htmlBaseDanger = '<div class="alert alert-danger" id="errorPanel">';
                        var htmlBaseSuccess = '<div class="alert alert-success" id="errorPanel">';
                        var htmlBaseEnd = '</div>';
                        if (data.success) {
                            html = htmlBaseSuccess;
                            html += '<div class="text-center"><h2>Post Successful</h2></div><dl><dt>Job</dt><dd><div class="form-group has-success"><input type="text" class="form-control" id="jobUrl" value="' + data.jobUrl + '" onclick="$(this).select();"></div></dd><dt>Company</dt><dd><div class="form-group has-success"><input type="text" class="form-control" id="companyUrl" value="' + data.companyUrl + '" onclick="$(this).select();"></div></dd><dt>Extend Job Link</dt><dd><div class="form-group has-success"><input type="text" class="form-control" id="deleteUrl" value="' + data.extendUrl + '" onclick="$(this).select();"></div></dd><dt>Delete Job Link</dt><dd><div class="form-group has-success"><input type="text" class="form-control" id="extendUrl" value="' + data.deleteUrl + '" onclick="$(this).select();"></div></dd></dl>';
                            html += htmlBaseEnd;
                            $('#formJob').trigger('reset');
                            $('#formNewCompany').trigger('reset');
                            $('#formExistingCompany').trigger('reset');
                        } else {
                            html = htmlBaseDanger;
                            html += data.e;
                            html += htmlBaseEnd;
                        }

                        $("#companyChoiceStart").prepend(html);
                        $(window).scrollTop(0);
                    });
                }
            });

    handler.open({
              name: 'VGJ Job Posting',
              description: '60 day job posting',
              currency: "usd",
              amount: 5000
            });
}

function extendJobX() {
    var handler = StripeCheckout.configure({
                key: 'pk_test_UMi9di6mRXqjM66nHnDY4TTx',
                image: '/img/documentation/checkout/marketplace.png',
                token: function(token) {
                    $("#stripeToken").val(token.id);
                    $("#extendForm").submit();
                }
            });

    handler.open({
              name: 'VGJ Job Posting Extension',
              description: '60 day job posting extension',
              currency: "usd",
              amount: 3500
            });
}