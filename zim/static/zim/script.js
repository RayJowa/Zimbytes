var data_set = {};

function addToCart(product_id) {

        $('.product-options div ul').each(function () {
            var att = $(this).children().first().children('span').text();
            data_set[att] = $('#'+att).val()
        });

        data_set['product']=product_id;
        data_set['quantity']=$('#quantity').val();
        data_set['csrfmiddlewaretoken']= $('input[name=csrfmiddlewaretoken]').val();
        console.log(data_set);
        $.ajax({
				url:'/add_to_cart/',
				method:'POST',
				data: data_set,
				success:function (data) {
				    $('#order_total').text(data.order_total);
                    $('#cart_count').text(data.order_count);
                    $('#qty').text(' x ' + $('#quantity').val());
                    $('#add_to_list').show();
                }
			});
    }



$(document).ready(function () {
    //set product attributes
    $('.size-option li').click(function () {
        $(this).addClass('active')
            .siblings('.active').removeClass('active');
        var value = $(this).children('a').text();
        $(this).parent().parent().children('input').val(value);
    });

    /*
    $('#add_to_cart').click(function () {
        addToCart()
    })*/

});