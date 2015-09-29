function getMoreRoundLogs() {
    $.get("/round/log", function(data) { $("#roundLogColumn").prepend(data); });
    getRoundProgress();
}

function getRoundProgress() {
    $.get("/round/progress", function(data) { 
        $('.dial').val(data.progress).trigger('change');
        $("#roundProgressAmount").html(data.progress_sum);
        $("#ig-balance-text").val(data.balance);
    });
}

function getWithdraw() {
    $("#withdrawColumns").html("");

    $.get("/betting/withdraw", function(data) { 
        $("#withdrawColumns").html(data);
        $("#withdrawForm").submit(function(event) {
            var formData = $("#withdrawForm").serialize();

            $.post("/betting/withdraw", formData, function(data) {
                if (data.success) {
                    $("#withdrawColumns").html("<p class='text-center bg-success'>" + data.message + "</p>");
                    setTimeout(function(){$("#withdrawColumns").html("");}, 30*1000);
                } else {
                    $("#withdrawFormError").html(data.message);
                }
                getMoreRoundLogs();
            });
            event.preventDefault();
        });
    });
}

function placeBet() {
    $("#betFormErrorDiv").hide();
    $("#betFormSuccessDiv").hide();

    var formData = $("#betForm").serialize();

    $.post("/betting/place", formData, function(data) {
        if (data.success) {
            $("#betFormSuccess").html(data.message);
            $("#betFormSuccessDiv").show();
            $("#ig-bet-text").val("");
        } else {
            $("#betFormError").html(data.message);
            $("#betFormErrorDiv").show();
        }
        $("#bettingModal").modal('toggle');
        getMoreRoundLogs();
    });
}

function infoModal(url) {
    $.get(url, function(data) {
        $("#infoBody").html(data);
        $("#infoModal").modal('toggle');
    });
}