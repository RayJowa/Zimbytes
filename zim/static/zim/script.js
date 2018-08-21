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

function removeFromCart(item_id) {

    $.ajax({
       url:'/delete_item/',
       method: 'POST',
       data: {
           csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
           item_id:item_id
       },
        success: function (data) {
            $('#item'+item_id).hide();
            $('#sub_total').text(data.order_total);
            $('#total').text(data.order_total);
        }
    });

};

function deleteFromCart(item_id) {
    $.ajax({
       url:'/delete_item/',
       method: 'POST',
       data: {
           csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
           item_id:item_id
       },
        success: function (data) {
            $('#item'+item_id).hide();
            $('#cart_count').text(data.order_count);
            $('#order_total').text(data.order_total);
        }
    });

};



function deleteOrder(order_id) {
    $.ajax({
       url:'/delete_order/',
       method: 'POST',
       data: {
           csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
           order_id:order_id
       },
        success: function (data) {
            $('#order'+order_id).hide();
        }
    });

}

function changeAffiliate() {
    $.ajax({
        url: '/change_affiliate/',
        method: 'POST',
        data: {
           csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
           affiliate: $('#affiliate').val()
        },
        success: function (data) {
            console.log(data);
        }
    })
}


function changeQuantity(item_id) {
    $.ajax({
        url: '/change_quantity/',
        method: 'POST',
        data:{
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            item_id: item_id,
            quantity: $('#qty'+item_id).val()
        },
        success: function (data) {
            $('#item_'+item_id+'_total').text(data.new_price);
            $('#sub_total').text(data.new_order_total);
            $('#total').text(data.new_order_total);
        }
    })

}

function nextTab(elem) {
    $(elem).next().find('a[data-toggle="tab"]').click();
}
function prevTab(elem) {
    $(elem).prev().find('a[data-toggle="tab"]').click();
}


$(document).ready(function () {
        //Initialize tooltips
    $('.nav-tabs > li a[title]').tooltip();

    //Wizard
    $('a[data-toggle="tab"]').on('show.bs.tab', function (e) {

        var $target = $(e.target);

        if ($target.parent().hasClass('disabled')) {
            return false;
        }
    });

    $(".next-step").click(function (e) {

        var $active = $('.wizard .nav-tabs li.active');
        $active.next().removeClass('disabled');
        nextTab($active);

    });
    $(".prev-step").click(function (e) {

        var $active = $('.wizard .nav-tabs li.active');
        prevTab($active);

    });

    //set product attributes
    $('.size-option li').click(function () {
        $(this).addClass('active')
            .siblings('.active').removeClass('active');
        var value = $(this).children('a').text();
        $(this).parent().parent().children('input').val(value);
    });

    $('#myBtn').click(function () {
        console.log('working');
        $('#myModal').show();

    });

    $('#close_modal').click(function () {
        $('#myModal').hide();
    });
    /*
    $('#add_to_cart').click(function () {
        addToCart()
    })*/

});