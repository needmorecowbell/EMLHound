$(document).ready( function () {
    $('#reports-table').DataTable({
        "scrollY":"50vh",
        "scrollCollapse": true,
        "order": [[1, 'desc']],
    });


    $(".action-delete-workspace").on("click", function(e) {
        let hash = $(this).parent().prev().text();
    
        $.ajax({
            url: "/report/"+hash,
            type: "DELETE"
        }).done(function(data) {
            location.reload();
        }).fail(function(response) {
            console.log("Error: ",response.status);
        });
    });
});
