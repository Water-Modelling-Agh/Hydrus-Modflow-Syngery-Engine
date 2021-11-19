(function($) {

    document.getElementById("form-create-project").onsubmit = function (e) {
        e.preventDefault()
        const name = this.elements.name.value;
        const lat = this.elements.lat.value;
        const long = this.elements.long.value;
        const startDate = this.elements.startDate.value;
        const endDate = this.elements.endDate.value;

        if( isTextCorrect(name,'name') &&
            isCoordCorrect(lat, 'lat') &&
            isCoordCorrect(long, 'long') &&
            isDateCorrect(startDate, 'startDate') &&
            isDateCorrect(endDate, 'endDate')){

            const formdata = {
                "name": name,
                "lat": lat,
                "long": long,
                "start_date": startDate,
                "end_date": endDate
            };

             $.ajax({
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify(formdata),
                        dataType: 'json',
                        url: Config.createProject,
                        success: function (e) {
                            $('#success-project-create').toast('show');
                            setTimeout(function () {
                                window.location.href = Config.currentProject;
                            }, 500);
                        },
                        error: function(error) {
                            const errorMsg = error.responseJSON.error;
                            addInvalid('name');
                            $('#toast-body-error').text(errorMsg);
                            $('#error').toast('show');
                    }
             });


        } else {
            $('#toast-body-error').text('Provide correct data')
            $('#error').toast('show');
        }
    }

    function isDateCorrect(date, elementId) {
        if(date.match(/^(19|20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$/g,date)){
            removeInvalid(elementId);
            return true;
        } else {
            addInvalid(elementId);
            return false;
        }
    }

    function isCoordCorrect(coord, elementId) {
        if(coord.match(/^[-]?(0|[1-9][0-9]*)([.]\d+)?$/g,coord)){
            removeInvalid(elementId);
            return true;
        } else {
            addInvalid(elementId);
            return false;
        }

    }

    function isTextCorrect(text, elementId) {
        if (text.trim() !== "" && text !== null && text !== undefined){
            removeInvalid(elementId);
            return true;
        } else {
            addInvalid(elementId);
            return false;
        }
    }

    function removeInvalid(elementId){
        if($(`#${elementId}`).hasClass('is-invalid')){
            $(`#${elementId}`).removeClass('is-invalid');
        }
    }

    function addInvalid(elementId){
        if(!$(`#${elementId}`).hasClass('is-invalid')){
                $(`#${elementId}`).addClass('is-invalid');
        }
    }
})(jQuery);
