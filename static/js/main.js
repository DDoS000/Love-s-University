(function($) {
	"use strict"
	
	// Preloader
	$(window).on('load', function() {
		$("#map").delay(600).fadeOut();
		$("#preloader").delay(600).fadeOut();
	});

	// Mobile Toggle Btn
	$('.navbar-toggle').on('click',function(){
		$('#header').toggleClass('nav-collapse')
	});
	
})(jQuery);