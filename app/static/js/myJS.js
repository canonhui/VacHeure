$(document).on('ready', function() {
	$('li.active').removeClass('active');
    current_path = location.pathname;
    if(current_path.split('/')[3]) {
    	current_path = '/' + current_path.split('/')[1] + '/' + current_path.split('/')[2];
    }

    else if(current_path == '/admin/add_user') {
    	current_path = '/admin/';
    }
    $('a[href="' + current_path + '"]').closest('li').addClass('active');
    $('a[href="' + current_path + '"]').css('color', '#f45');
    
    if(location.pathname == '/') {
        $('a[href="/index"]').closest('li').addClass('active');
        $('a[href="/index"]').css('color', '#f45');
    }


	//var affiche_div = $('.affiche-div').attr('class').split(' ');
	//var classes = {'bp': affiche_div[1], 'template_flag': affiche_div[2], 'page': affiche_div[3], 'app_name': affiche_div[4]};
	

	function motif_rejet_fade_in(obj) {
		var select_id = obj.attr('id');
		var motif_rejet_id = obj.parents('tr').find('.motif-rejet').attr('id');
		if($('#' + select_id + ' ' + 'option:selected').attr('value') == -1) {
			$('#' + motif_rejet_id).fadeIn(300);
			$('#' + motif_rejet_id + ' textarea').focus();
		}
		else {
			$('#' + motif_rejet_id + ' textarea').val('');
		}
	}


	$('.affiche-div').on('change', 'select.valid-checkbox', function() {
		motif_rejet_fade_in($(this));
	})

	$('.affiche-div').on('click', '.motif-lien', function() {
		var obj = $(this).prev();
		motif_rejet_fade_in(obj);
	})

	$('.affiche-div').on('mouseover', '.valid-div', function() {
		var select_id = $(this).find('select').attr('id');
		if($('#' + select_id + ' ' + 'option:selected').attr('value') == -1) {
			$(this).find('.motif-lien').show(300);
		}
	})
	$('.affiche-div').on('mouseleave', '.valid-div', function() {
		$('.motif-lien').hide(300);
	})

	$('.affiche-div').on('click', '.btn-motif-rejet', function() {
		var motif_rejet_id = $(this).parents('section').attr('id');
		if($('#' + motif_rejet_id + ' ' + 'textarea').val() ==  '') {
			$('#' + motif_rejet_id + ' ' + '.warning-msg').html('Un motif est obligatoire<br>');
		}
		else {
			$(this).parents('section').fadeOut(300);
		}
	})

	$('.affiche-div').on('input propertychange', 'textarea', function() {
		if($(this).val() != '') {
			$(this).prev().html('');
		}
	})


    $('.affiche-div').on('click', '.fond', function(){
        var select_id = $(this).parents('td').find('select').attr('id');
        $('#' + select_id).parent().next().find('textarea').val('');
        $('#' + select_id).parent().next().find('.warning-msg').html('');
        $(this).parent().fadeOut(300);
        $('#' + select_id).val('0');
    });
    $('.affiche-div').on('click', '.UI', function(e){
        e.stopPropagation();
    });


    $('#login').val('');
    $('.form-edit-user').on('input propertychange', '#login', function() {
        var login = $(this).val();
        if(login == '') {
            $('.info-msg').text();
            $('#prenom').val('');
            $('#nom').val('');
            $('#email').val('');
            $('.btn-update-user').attr('value', 'Updater');
        }
        else {
            $.ajax({
                url: "/admin/edit_user",
                data: {login: login},
                type: 'GET',
                dataType: 'json',
                success: function(data) {
                    //$('#prenom').focus();
                    if(data['msg']) {
                        $('.info-msg').text(data['msg']);
                        $('#prenom').val('');
        				$('#nom').val('');
       					$('#email').val('');
       					$('#role').val('1');
        				$('.btn-update-user').attr('value', 'Ajouter');

		        		
                    }
                    else {
                        $('.info-msg').text('');
                        $('#prenom').val(data['prenom']);
			            $('#nom').val(data['nom']);
			            $('#email').val(data['email']);
			            $('#role').val(data['role']);
			            $('#dept').val(data['dept']);
        				$('.btn-update-user').attr('value', 'Updater');
                    }
                }
            })
        }
    });
    $('#nom, #prenom').on('input propertychange', function() {
    	if($('.btn-update-user').attr('value') == 'Ajouter') {
			var email_data = $('#prenom').val() + '.' + $('#nom').val() + '@esiee.fr';
			$('#email').val(email_data.toLowerCase());
			$('#login').val(login_data.toLowerCase());
		}
    });


	if(current_path.split('/')[2]=='validation_email') {
		var etat = $('.validation-email').attr('class').split(' ')[1];
		if(etat == -1) {
			$('.motif-rejet').show();
			$('.motif-rejet textarea').focus();

			$('.validation-email').on('click', '.btn-motif-rejet', function() {
				var motif_rejet_id = $(this).parents('section').attr('id');
				if($('#' + motif_rejet_id + ' ' + 'textarea').val() ==  '') {
					$('#' + motif_rejet_id + ' ' + '.warning-msg').html('Un motif est obligatoire<br>');
				}
				else {
					var motif_rejet_ajax = $('#' + motif_rejet_id + ' ' + 'textarea').val();
					var pseudo_ajax = $('.motif-rejet').attr('class').split(' ')[1];
					var id_ajax = $('.motif-rejet').attr('class').split(' ')[2];
					var app = location.pathname.split('/')[2];
					$.ajax({
						url: location.pathname,
		                data: {motif_rejet: motif_rejet_ajax},
		                type: 'POST',
		                success: function(response) {
							$('.motif-rejet').fadeOut(300);
							$('.main-info').fadeIn(300);
							time_counter();
		                }
					});
				}
			});

			$('.validation-email').on('input propertychange', 'textarea', function() {
				if($(this).val() != '') {
					$(this).prev().html('');
				}
			});

		}

		else {
			$('.main-info').fadeIn();
			time_counter();
		}

	    var timeout = 5;
	    function time_counter() {
	    	timeout--;
	    	if(timeout == 0) {
	    		window.open('','_parent','');
	    		window.close();
	    	}
	    	else {
	    		setTimeout(time_counter, 1000);
	    	}
	    	$('.validation-email .seconds').html(timeout);
	    }
	}

})

function remiseAZeroForm(obj) {
	var base = obj.attr('class').split(' ')[2];
	if(confirm('En cliquant "OK", vous allez supprimer tous les contenus de la base ' + base + ' !') == false) {
		return false;
	}
}

function deleteUserForm(obj) {
	var login = obj.parents('form').find('#login').val();
	if(login && confirm('En cliquant "OK", vous allez supprimer l\'utilisateur ' + login + ' !') == false) {
		return false;
	}
}