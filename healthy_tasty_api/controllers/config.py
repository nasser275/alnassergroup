def validate_data(token,config_token):
    response = {}
    if token != config_token:
        response['result'] = []
        response['message'] = 'Healthy and Tasty Token Invalid.'
        response['status'] = 301
    return response


def get_image_url(base, categ_id):
    return base + '/web/image?model=product.public.category&id=%s&field=image_256' % categ_id,

def get_image_url_512(base, categ_id):
    return base + '/web/image?model=product.public.category&id=%s&field=image_512' % categ_id,


def get_image_url_for_prod(base, prod_id):
    return base + '/web/image?model=product.product&id=%s&field=image_256' % prod_id,

def get_image_url_for_sliders(base, slid_id):
    return base + '/web/image?model=api.sliders&id=%s&field=image' % slid_id,
def get_image_url_for_user(base, user_id):
    return base + '/web/image?model=res.users&id=%s&field=image_256' % user_id

def get_image_url_for_testimonials(base, testimonial_id):
    return base + '/web/image?model=api.testimonials&id=%s&field=image' % testimonial_id,