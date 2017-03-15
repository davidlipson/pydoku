$(document).ready(function(){
	$('textarea').val("");
	$('#solve').click(function(){
		var string = "";
		$('textarea').each(function(a){
			if ($(this).val() == ""){
				string += "_";
			}else{
				string += String($(this).val());
			}
		});
		$("#info").html("<div id=\"info\" class=\"alert alert-warning\">Loading...</div>");
		$.ajax({
			url: '/py/solve',
			type: "POST",
			data: JSON.stringify({
				"string": string
			}),
			contentType: "application/json; charset=utf-8",
			success: function(response){
				$("#info").html("<div id=\"info\" class=\"alert alert-success\">Success!</div>");
				$('textarea').each(function(a){
					if (string[a] != "_"){
						$(this).css('color', "blue");
					}
					$(this).val(response[a]);
				});
			},
			error: function(err){
                                $("#info").html("<div id=\"info\" class=\"alert alert-danger\">Error!</div>");
			}

		});
	});
	
	$("textarea").focus(function(){
		var obj = $(this);
		$(this).on("keypress", function (e) {
			if($(this).parent().next().length == 0){
				$(this).parent().parent().next().children().first().children().first().trigger('focus');
			}else{
				$(this).parent().next().children().first().trigger('focus');
			}
		});
	});
});
