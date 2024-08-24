from odoo import fields, models, api
from odoo.http import Controller, request, route
import requests, logging, time, socket

HealthyToken = 'k87d5883-8344-4623-u763-7n46449a'
import calendar, time, functools, threading


def timer(func):
    @functools.wraps(func)
    def function_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        # if run_time >= 1:
        print("finished {} in {}".format(func.__name__, run_time))
        return value

    return function_timer


# def _validate_data(data, relational_fields={}, required_parameter=[]):
# 	response = {}
# 	param_models = {'company_id': 'res.company'}
# 	if data.get('token') != HealthyToken:
# 		response['result'] = []
# 		response['message'] = 'Invalid token.'
# 		response['status'] = 301
# 	if required_parameter:
# 		for param in required_parameter:
# 			if not param in data:
# 				response['message'] = '{} parameter is missing.'.format(param)
# 				response['status'] = 404
# 	if relational_fields:
# 		for field,model in relational_fields.items():
# 			if field in data and data.get(field):
# 				print('param, model',key,model)
# 				found_data = request.env[model].sudo().search([('id', '=', data.get(field))],limit=1)
# 				if not found_data:
# 					response['result'] = []
# 					response['message'] = "{} value ({}) not found in database please insert correct id.".format(field, data.get(field))
# 					response['status'] = 404
# 			else:
# 				response['message'] = "{} parameter is missing or doesn't has a value.".format(field)
# 				response['status'] = 404
# 	return response

# def timer_func(func):
#     # This function shows the execution time of
#     # the function object passed
#     def wrap_func(*args, **kwargs):
#         t1 = time()
#         result = func(*args, **kwargs)
#         t2 = time()
#         print('Function {name} executed in {value}s'.format(name=func.__name__,value=t2-t1))
#         return result
#     return wrap_func

def try_except_decorator(func):
    response = {}

    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            response['message'] = "{e}".format(e=e)
            return response

    return wrapper


@timer
def _validate_data(data, relational_fields={}, required_parameter=[], validate_selection={}):
    response = {}
    required = _required_parameters(data, required_parameter)
    if 'message' in required:
        response['message'] = required['message']
        response['status'] = required['status']
    relational = _relational_fields(data, relational_fields)
    if 'message' in relational:
        response['message'] = relational['message']
        response['status'] = relational['status']
    selections = _validate_selection_options(data, validate_selection)
    if 'message' in selections:
        response['message'] = selections['message']
        response['status'] = 422
    return response


@timer
def _validate_selection_options(data, validate_selection):
    response = {}
    if validate_selection:
        for key, value in validate_selection.items():
            if key in data and data.get(key) not in value:
                response['message'] = "wrong value for parameter ({}) you should use one of these values {}.".format(
                    key, value)
    return response


@timer
def _required_parameters(data, required_parameter):
    response = {}
    if required_parameter:
        for param in required_parameter:
            if not param in data:
                response['message'] = '{} parameter is missing.'.format(param)
                response['status'] = 404
            if param == 'limit' and not isinstance(data.get('limit'), int):
                response['message'] = '{} parameter must be integer.'.format(
                    param)
                response['status'] = 200
            if param == 'token' and data.get('token') != HealthyToken:
                response['result'] = []
                response['message'] = 'Invalid token.'
                response['status'] = 301
    return response


@timer
def _relational_fields(data, relational_fields):
    response = {}
    if relational_fields:
        for field, model in relational_fields.items():
            # print('data.get(field)', data.get(field))
            if field in data and data.get(field):
                if not isinstance(model, dict):
                    found_data = request.env[model].search(
                        [('id', '=', data.get(field))], limit=1)
                else:
                    if 'domian' in model and model.get('domian'):
                        found_data = request.env[model.get('model')].search(
                            [('id', '=', data.get(field))] + model.get('domian'), limit=1)
                    else:
                        found_data = request.env[model.get('model')].search(
                            [('id', '=', data.get(field))], limit=1)
                if not found_data:
                    response['result'] = []
                    response['message'] = "{} value ({}) not found in database please insert correct id.".format(
                        field, data.get(field))
                    response['status'] = 404
            else:
                response['message'] = "{} parameter is missing or doesn't has a value.".format(
                    field)
                response['status'] = 404

    print('_relational_fields', response)
    return response
