$(function(){

	var imagefields = [document.getElementById("image1"),
					document.getElementById("image2"),
					document.getElementById("image1_mobile"),
					document.getElementById("image2_mobile")];

	resemble.outputSettings({
		transparency: 0.3
	});

	resemble.outputSettings({
		errorType: 'movementDifferenceIntensity'
	});

	var resembleControl;
	var resembleControl2;

	var imagesdict = {};
	for (var i=0; i< imagefields.length; i++){
		getBase64FromImageUrl(imagefields[i]);
	}

	function getBase64FromImageUrl(image) {

	    function loadHandler() {
	        var canvas = document.createElement("canvas");
	        canvas.width =this.width;
	        canvas.height =this.height;

	        var ctx = canvas.getContext("2d");
	        ctx.drawImage(image, 0, 0);
	        var dataURL = canvas.toDataURL("image/png");
	        imagesdict[imagefields.indexOf(image)] = dataURL;
	        console.log("loaded");

        	image.onclick = function(){
				window.open(image.src, '_blank');
			};

	        if(Object.keys(imagesdict).length == 4){
	        	console.log(imagesdict)
				resembleControl = resemble(imagesdict[0]).compareTo(imagesdict[1]).onComplete(onComplete);
				resembleControl2 = resemble(imagesdict[2]).compareTo(imagesdict[3]).onComplete(onComplete);
				$('.buttons').show();
				available_width = $('#img_frame').width();
				width1 = $('#image1').width();
				width2 = $('#image1_mobile').width();
				mobile_proportion = width2 / $('#image1_mobile').height();
			    mobile_width_adjust = mobile_proportion * $('#image1').height();
			    width_proportion = (available_width-5) / (mobile_width_adjust + width1);
				$('#image1').width(width1 * width_proportion +"px");
				$('#image1_mobile').width(mobile_width_adjust * width_proportion  +"px");
				width1 = $('#image2').width();
				width2 = $('#image2_mobile').width();
				mobile_proportion = width2 / $('#image2_mobile').height();
			    mobile_width_adjust = mobile_proportion * $('#image2').height();
			    width_proportion = (available_width-5) / (mobile_width_adjust + width1);
				$('#image2').width(width1 * width_proportion +"px");
				$('#image2_mobile').width(mobile_width_adjust * width_proportion  +"px");

			}
	    };

	    if (image.complete) {
        	loadHandler();
    	} else {
	    	image.onload = loadHandler;
    	}

	}

	function onComplete(data){
		var img = new Image();
		$('#loading').remove();
		img.onload = function() {
			if(this.width > 600) {
				parent = $('#image-diff');
				diff_img = $('#diff1');

				if(data.misMatchPercentage === 0){
					$('#thesame').show();
					$('#identical').show();
					$('#diff-results').hide();
				} else {
					$('#mismatch').text(data.misMatchPercentage);
					if(!data.isSameDimensions){
						$('#differentdimensions').show();
					} else {
						$('#differentdimensions').hide();
					}
					$('#diff-results').show();
					$('#thesame').hide();
					$('#identical').hide();
				}
			}else{
				parent = $('#image-diff2');
				diff_img = $('#diff2');

				if(data.misMatchPercentage === 0){
					$('#thesame2').show();
					$('#identical2').show();
					$('#diff-results2').hide();
				} else {
					$('#mismatch2').text(data.misMatchPercentage);
					if(!data.isSameDimensions){
						$('#differentdimensions2').show();
					} else {
						$('#differentdimensions2').hide();
					}
					$('#diff-results2').show();
					$('#thesame2').hide();
					$('#identical2').hide();
				}
			}
			if((data.diffBounds.bottom-data.diffBounds.top) > 500){
				$('#down').show();
			}
		  	available_width = parent.width();
			diff_proportion =  this.width/available_width;
			diff_img.width(available_width);
			parent.height((data.diffBounds.bottom/diff_proportion-data.diffBounds.top/diff_proportion)+100 );
		    diff_img.css('top' , -(data.diffBounds.top/diff_proportion)+50+"px");
		    diff_img.css('bottom', -(data.diffBounds.bottom/diff_proportion)-50+"px");
		    diff_img.attr('src', img.src);

			parent.click(function(){
				window.open(img.src, '_blank');
			});
		};
		console.log(data);
		img.src = data.getImageDataUrl();
	}

	var buttons = $('.buttons button');

	buttons.click(function(){
		var $this = $(this);

		$this.parent('.buttons').find('button').removeClass('active');
		$this.addClass('active');

		if($this.is('#raw')){
			$('.diffimg').removeAttr('src');
			resembleControl.ignoreNothing();
			resembleControl2.ignoreNothing();
		}
		else
		if($this.is('#colors')){
			$('.diffimg').removeAttr('src');
			resembleControl.ignoreColors();
			resembleControl2.ignoreColors();
		}
		else
		if($this.is('#antialising')){
			$('.diffimg').removeAttr('src');
			resembleControl.ignoreAntialiasing();
			resembleControl2.ignoreAntialiasing();
		}
		else
		if($this.is('#same-size')){
			$('.diffimg').removeAttr('src');
			resembleControl.scaleToSameSize();
			resembleControl2.scaleToSameSize();
		}
		else
		if($this.is('#original-size')){
			$('.diffimg').removeAttr('src');
			resembleControl.useOriginalSize();
			resembleControl2.useOriginalSize();
		}
		else
		if($this.is('#pink')){
			resemble.outputSettings({
				errorColor: {
					red: 255,
					green: 0,
					blue: 255
				}
			});
			$('.diffimg').removeAttr('src');
			resembleControl.repaint();
			resembleControl2.repaint();
		}
		else
		if($this.is('#yellow')){
			resemble.outputSettings({
				errorColor: {
					red: 255,
					green: 255,
					blue: 0
				}
			});
			$('.diffimg').removeAttr('src');
			resembleControl.repaint();
			resembleControl2.repaint();
		}
		else
		if($this.is('#flat')){
			resemble.outputSettings({
				errorType: 'flat'
			});
			$('.diffimg').removeAttr('src');
			resembleControl.repaint();
			resembleControl2.repaint();
		}
		else
		if($this.is('#movement')){
			resemble.outputSettings({
				errorType: 'movement'
			});
			$('.diffimg').removeAttr('src');
			resembleControl.repaint();
			resembleControl2.repaint();
		}
		else
		if($this.is('#flatDifferenceIntensity')){
			resemble.outputSettings({
				errorType: 'flatDifferenceIntensity'
			});
			$('.diffimg').removeAttr('src');
			resembleControl.repaint();
			resembleControl2.repaint();
		}
		else
		if($this.is('#movementDifferenceIntensity')){
			resemble.outputSettings({
				errorType: 'movementDifferenceIntensity'
			});
			$('.diffimg').removeAttr('src');
			resembleControl.repaint();
			resembleControl2.repaint();
		}
		else
		if($this.is('#opaque')){
			resemble.outputSettings({
				transparency: 1
			});
			$('.diffimg').removeAttr('src');
			resembleControl.repaint();
			resembleControl2.repaint();
		}
		else
		if($this.is('#transparent')){
			resemble.outputSettings({
				transparency: 0.3
			});
			$('.diffimg').removeAttr('src');
			resembleControl.repaint();
			resembleControl2.repaint();
		}
	});

});