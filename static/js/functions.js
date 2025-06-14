console.log ("working...")


$(document).ready(function(){
    const Toast = Swal.mixin({
        toast: true,
        position: "top",
        showConfirmButton: false,
        timer: 2000,
        timerProgressBar: true,
    });

    function generateCartId(){
        const ls_cartid = localStorage.getItem("cartId");

        if (ls_cartid === null) {
            var cartId = "";

            for (var i = 0; i < 10; i++) {
                cartId += Math.floor(Math.random()*10)
            }

            localStorage.setItem("cartId", cartId);
        }

        return ls_cartid || cartId
    }

    $(document).on("click", ".add_to_cart", function (e){
        e.preventDefault();
        const button_el = $(this)
        const id = button_el.attr("data-id")

        let qty = $(this).closest(".product-bottom-action").find("input.quantity").val();
        qty = qty && !isNaN(qty) && Number(qty) > 0 ? qty : 1;

        // const qty = $(this).closest(".product-bottom-action").find("input.quantity").val();
        const size = $("input[name='size']:checked").val()
        const color = $("input[name='color']:checked").val()
        const cart_id = generateCartId()

        $.ajax({
            url:"/add_to_cart/",
            data: {
                id: id,
                qty: qty,
                size:size,
                color: color,
                cart_id: cart_id
                
            },
            beforeSend: function(){
                button_el.html("Adding to cart <i class='fas fa-spinner fa-spin ms-2'></i>");
            },
            success: function(response){
                console.log(response);
                Toast.fire({
                    icon: "success",
                    title: response?.message,
                });
                button_el.html("Add To Cart <i class='rt-basket-shopping ms-2'></i>");
                $(".total_cart_items").text(response?.total_cart_items);

            },
            error: function(xhr, status, error){
                console.log("Error status: ", xhr.status);
                console.log("Response text: ", xhr.responseText);

                let errorResponse = JSON.parse(xhr.responseText);
                Toast.fire({
                    icon: "success",
                    title: errorResponse?.error,
                });
            }
        });
    });

    $(document).on("click", ".update_cart_qty", function (e) {
        const button_el = $(this);
        const update_type = button_el.attr("data-update_type");
        const product_id = button_el.attr("data-product_id");
        const item_id = button_el.attr("data-item_id");
        const cart_id = generateCartId();
    
        // Prevent rapid double-click
        if (button_el.prop('disabled')) return;
    
        let currentQty = parseInt($(".item-qty-" + item_id).val());
        let newQty = update_type === "increase" ? currentQty + 1 : Math.max(currentQty - 1, 1);
    
        $.ajax({
            url: "/add_to_cart/",
            data: {
                id: product_id,
                qty: newQty,
                cart_id: cart_id
            },
            beforeSend: function () {
                button_el.prop("disabled", true).html("<i class='fas fa-spinner fa-spin ms-2'></i>");
            },
            success: function (response) {
                Toast.fire({
                    icon: "success",
                    title: response?.message,
                });
    
                // Update qty and prices in UI
                $(".item-qty-" + item_id).val(newQty);
                $(".item_sub_total_" + item_id).text(response.item_sub_total);
                $(".cart_sub_total").text(response.cart_sub_total);
    
                button_el.prop("disabled", false).html(update_type === "increase"
                    ? '<i class="fal fa-plus plus"></i>'
                    : '<i class="fal fa-minus minus"></i>');
            },
            error: function (xhr) {
                let errorResponse = JSON.parse(xhr.responseText);
                Toast.fire({
                    icon: "error",
                    title: errorResponse?.error,
                });
    
                button_el.prop("disabled", false).html(update_type === "increase"
                    ? '<i class="fal fa-plus plus"></i>'
                    : '<i class="fal fa-minus minus"></i>');
            }
        });
    });
    
   


    $(document).on("click", ".delete_cart_item", function(){
        const button_el = $(this);
        const item_id = button_el.attr("data-item_id");
        const product_id = button_el.attr("data-product_id");
        const cart_id = generateCartId();

        $.ajax({
            url: "/delete_cart_item/",
            data: {
                id: product_id,
                item_id: item_id,
                cart_id: cart_id,
            },
            beforeSend: function(){
                button_el.html("<i class='fas fa-spinner fa-spin ms-2'></i>");
            },
            success: function(response){
                console.log(response);
                Toast.fire({
                    icon: "success",
                    title: response?.message,
                });
                
                $(".total_cart_items").text(response?.total_cart_items);
                $(".cart_sub_total").text(response?.cart_sub_total);
                $(".item_div_"+item_id).addClass("d-none");
            },

        })
    })

});

