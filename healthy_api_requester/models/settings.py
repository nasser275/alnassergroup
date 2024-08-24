from odoo import fields, models, api
import requests
import socket
import logging

_logger = logging.getLogger(__name__)
LIVE_IP_ADDRESS = "157.230.96.56"
TEST_IP_ADDRESS = "147.182.192.42"
LIVE_DOMAIN = "http://admin.healthyandtasty.net"
# LIVE_DOMAIN = "http://demoadmin.healthyandtasty.net"
TEST_DOMAIN = "http://demoadmin.healthyandtasty.net"


def get_domain_for_host_by_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    if ip_address == LIVE_IP_ADDRESS:
        return LIVE_DOMAIN
    else:
        return TEST_DOMAIN


def chec_ip_is_live():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()
    if ip_address == LIVE_IP_ADDRESS:
        return True
    else:
        return False


def get_image_url_512_for_categ(base, categ_id):
    return base + '/web/image/product.category/%s/image_medium' % categ_id


# env(user=SUPERUSER_ID)

def get_image_url_for_prod(base, prod_id):
    return base + '/web/image/product.product/%s/image_1920' % prod_id
