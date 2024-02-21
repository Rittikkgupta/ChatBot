
from django.http import JsonResponse
import requests
import json
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import requests
import os
import uuid
from datetime import datetime
import logging
from rest_framework import status
from dateutil import parser
import pyodbc
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate
from django.http import JsonResponse
from requests import Session
#import google.cloud.dialogflow_v2 as dialogflow
#from google.oauth2 import service_account

from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
import requests
import json
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import requests
import os
import uuid
from datetime import datetime
import logging
from rest_framework import status
from dateutil import parser
import pyodbc
from django.contrib.sessions.models import Session as DjangoSession
from django.contrib.auth import authenticate
from django.http import JsonResponse
from requests import Session as RequestsSession



logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class DialogflowWebhook(View):   
    logger = logging.getLogger(__name__)

    def __init__(self):
        super(DialogflowWebhook, self).__init__()
        token = None

    def post(self, request, *args, **kwargs):
        try:
            request_data = json.loads(request.body.decode('utf-8'))
            intent_display_name = request_data['queryResult']['intent']['displayName']
            print('intent_display_name', intent_display_name)

            # Check if the context for trying again is present
            '''contexts = request_data.get('queryResult', {}).get('outputContexts', [])
            try_again_context_present = any(context['name'].endswith('/contexts/try_again_transfer_date') for context in contexts)

            RID_try_again_context_present = any(context['name'].endswith('/contexts/try_again_Bookings_Request') for context in contexts)
'''
            if intent_display_name == 'Default Welcome Message':
                response_data = self.handle_verify_user_intent(request_data)
                '''response_data = {
                    'followupEventInput': {
                        'name': 'WELCOME',  # Event name defined in Dialogflow
                        'languageCode': 'en-US',  # Language code (adjust accordingly)
                    },
                }'''
            elif intent_display_name == 'Main menu':
                response_data = self.handle_Main_menu_intent(request_data)
            elif intent_display_name == 'Default Welcome Intent':
                response_data = self.handle_verify_user_intent(request_data)
            elif intent_display_name == 'Bookings_TransferDate' :
                response_data = self.handle_transfer_date_intent(request_data)
            elif intent_display_name == 'Request ID' :
                response_data = self.handle_Request_ID_intent(request_data)
            elif intent_display_name == 'Edit' :
                response_data = self.handle_Edit_intent(request_data)
            elif intent_display_name == 'More' :
                response_data = self.handle_more_intent(request_data)
            elif intent_display_name == 'bookingdetails':
                response_data = self.handle_bookingdetails_intent(request_data)
            elif intent_display_name == 'Cost price':
                response_data = self.handle_cost_price_intent(request_data)
            elif intent_display_name == 'transfertype':
                response_data = self.handle_transfer_type_intent(request_data)
            elif intent_display_name == 'confno':
                response_data = self.handle_conf_no_intent(request_data)
                
            elif intent_display_name == 'Status':
                response_data = self.handle_status_intent(request_data)
            elif intent_display_name == 'drivername':
                response_data = self.handle_driver_name_intent(request_data)
            elif intent_display_name == 'overridecost':
                response_data = self.handle_override_cost_intent(request_data)
            elif intent_display_name == 'starttime':
                response_data = self.handle_start_time_intent(request_data)
            elif intent_display_name == 'endtime':
                response_data = self.handle_end_time_intent(request_data)
            elif intent_display_name == 'remark':
                response_data = self.handle_remark_intent(request_data)
            elif intent_display_name == 'parkingfee':
                response_data = self.handle_parking_intent(request_data)
            elif intent_display_name == 'All Edit':
                response_data = self.handle_all_edit_intent(request_data)
            
            else:
                self.logger.warning("Invalid intent")
                return JsonResponse({'fulfillmentText': 'Invalid intent'})
            return JsonResponse(response_data)

        except json.JSONDecodeError as e:
            self.logger.error({'fulfillmentText': f'Error decoding JSON: {str(e)}'})
            return JsonResponse({'fulfillmentText': f'Error decoding JSON: {str(e)}'})
        except Exception as e:
            self.logger.error({'fulfillmentText': f'Error: {str(e)}'})
            return JsonResponse({'fulfillmentText': f'Error: {str(e)}'})


    def handle_verify_user_intent(self, request_data):
        try:
            external_api_url = 'http://150.242.13.125:9092/verify/'
            external_api_data = {
                'username': "sam",
                'password': "12345",
            }
            #
            print("request", request_data)

            headers = {
                'Content-Type': 'application/json',
            }

            # Make the API request using requests library
            external_api_response = requests.post(external_api_url, json=external_api_data, headers=headers, verify=False)
            response_json = external_api_response.json()

            if external_api_response.status_code == 200:
                token = response_json.get('data', [])[0].get('token', '')
                print("login", token)
                response_data = {
                                'fulfillmentMessages': [
                                    {
                                        'text': {
                                            'text': [
                                                f"Welcome to Tawfeeq Holidays!\n"
                                            ]
                                        }
                                    },
                                    {
                                        'text': {
                                            'text': [
                                                f"Please Enter Booking Request date in this Format YY/MM/DD"
                                            ]
                                        }
                                    }
                                ],  # <-- This closing bracket was missing
                                'followupEventInput': {
                                    'name': 'WELCOME',  # Event name defined in Dialogflow
                                    'languageCode': 'en-US',  # Language code (adjust accordingly)
                                },
                                'outputContexts': [
                                    {
                                        # 'name': f'{request_data["session"]}/contexts/token-context',
                                        'name': f'{request_data["session"]}/contexts/token-context',
                                        'lifespanCount': 10 * 60,  # Set the lifespan as needed
                                        'parameters': {'token': token},
                                    }
                                ]
                            }


                self.logger.info(f"Successful login attempt: {response_data}")
                return response_data
            else:
                self.logger.info(f'User Credential is Invalid. Status code: {external_api_response.status_code}')
                response_data = {
                    'fulfillmentMessages': [
                        {
                            'text': {
                                'text': [f'User Credential is Invalid. Status code: {external_api_response.status_code}']
                            }
                        },
                        {
                            'payload': {
                                'richContent': [
                                    [
                                        {'type': 'chips', 'options': [
                                            {'text': 'Main Menu'},
                                            {'text': 'Try Again-Login'}
                                        ]}
                                    ]
                                ]
                            }
                        }
                    ]
                }
                return response_data
        except Exception as e:
            self.logger.error(f'An error occurred during user verification: {str(e)}')
            return {'fulfillmentText': f'An error occurred during user verification: {str(e)}'}

    def handle_transfer_date_intent(self, request_data):
        try:
            token_context = next(
                (context for context in request_data.get('queryResult', {}).get('outputContexts', []) if 'token-context' in context.get('name', '')),
                {}
            )
            token = token_context.get('parameters', {}).get('token', None)

            transferdate_context = next(
                (context for context in request_data.get('queryResult', {}).get('outputContexts', []) if 'transferdate' in context.get('name', '')),
                {}
                )
            transferdate = transferdate_context.get('parameters', {}).get('transferdate', None)
            print("transferdate_context", transferdate_context)
            print("transferdate", transferdate)
            '''dialogflow_params = request_data.get('queryResult', {})
            transferdate = str(dialogflow_params.get('parameters', {}).get('Date', None))'''
            #print("transferdate", transferdate)
            if transferdate is None:
                dialogflow_params = request_data.get('queryResult', {})
                transferdate = str(dialogflow_params.get('parameters', {}).get('Date', None))
            transferdate_datetime = parser.isoparse(transferdate)
            formatted_transferdate = transferdate_datetime.strftime('%Y-%m-%d')

            # Your existing code for making the external API request
            external_api_url = 'http://150.242.13.125:9092/bookings/'
            external_api_data = {'transferdate': formatted_transferdate}

            

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
                'Google-Cloud-Project-Id': 'loginchatbot-gpht',
                'Google-Cloud-Project-Number': '679349695458',
            }

            external_api_response = requests.post(external_api_url, json=external_api_data, headers=headers, verify=False)

            if external_api_response.status_code == 200:
                external_api_data = external_api_response.json()
                bookings = external_api_data.get('data', [])
                booking_buttons = [
                    {
                        'text': f"{i + 1} Request ID: {booking.get('requestid', 'Unknown')}",
                        'event': {
                            'name': 'VIEW_BOOKING_EVENT',
                            'languageCode': 'en',
                            'parameters': {'booking_id': booking.get('requestid')}
                        }
                    }
                    for i, booking in enumerate(bookings)
                ]
                response_data = {
                    'fulfillmentMessages': [{
                                        'text': {
                                            'text': [
                                                f"Bookings are Available on\n"
                                                f"{formatted_transferdate}"
                                            ]
                                        }
                                    },
                        {
                            'payload': {
                                'richContent': [
                                    [
                                        {
                                            'type': 'chips',
                                            'options': booking_buttons + [
                                                {'text': 'I want to see again Booking List', 'intent': 'Bookings_TransferDate'}
                                            ]
                                        }
                                    ]
                                ]
                            }
                        }
                    ],
                    "outputContexts": [
                        {
                            "name": f"{request_data['session']}/contexts/transferdate",
                            "lifespanCount":20,  # Set the lifespan as needed
                            "parameters": {"transferdate": formatted_transferdate}
                        }
                        
                    ]
                }

                self.logger.info(f"Successful data fetched for {formatted_transferdate}: {response_data}")
                return response_data


            else:
                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [f'No bookings Request available on this date. Status code: {external_api_response.status_code}']}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Please Enter Booking Request date in this Format YY/MM/DD', 'intent': 'Bookings_TransferDate'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                                        ]
                                }
                self.logger.info(f"No bookings on {formatted_transferdate}: {response_data}")
                return response_data

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.warning(f"Error during data fetched for {formatted_transferdate}: {response_data}")
            return response_data
    

    def handle_Request_ID_intent(self, request_data):
        try:
            dialogflow_params = request_data.get('queryResult', {})
            requestid = str(dialogflow_params.get('parameters', {}).get('request_id', ''))

            transferdate_context = next(
                (context for context in request_data.get('queryResult', {}).get('outputContexts', []) if 'transferdate' in context.get('name', '')),
                {}
            )
            transferdate = transferdate_context.get('parameters', {}).get('transferdate', None)
            print("transferdate RID", transferdate)
            print("transferdate_context RID", transferdate_context)

            # Create the final Dialogflow response
            response_data = {
                "fulfillmentMessages": [
                    {
                        "payload": {
                            "richContent": [
                                [
                                    {
                                        "type": "chips",
                                        "options": [
                                            {"text": "View"},
                                            {"text": "All Edit"},
                                            {"text": "I want to see again Request id"},
                                        ]
                                    }
                                ]
                            ]
                        }
                    }
                ],
                "outputContexts": [
                    {
                        "name": f"{request_data['session']}/contexts/request_id",
                        "lifespanCount": 50,  # Set the lifespan as needed
                        "parameters": {"request_id": requestid}
                    }
                ]
            }

            return response_data
        except Exception as e:
            return {'fulfillmentText': f'An error occurred: {str(e)}'}

    def handle_bookingdetails_intent(self, request_data):
        try:
            token_context = next(
                (context for context in request_data.get('queryResult', {}).get('outputContexts', []) if 'token-context' in context.get('name', '')),
                {}
            )
                
            '''transferdate_context = next(
                (context for context in request_data.get('queryResult', {}).get('outputContexts', []) if 'transferdate' in context.get('name', '')),
                {}
            )
            transferdate = transferdate_context.get('parameters', {}).get('transferdate', None)'''
            
            request_id_context = next(
                (context for context in request_data.get('queryResult', {}).get('outputContexts', []) if 'request_id' in context.get('name', '')),
                {}
            )
            request_id = request_id_context.get('parameters', {}).get('request_id', None)

            token = token_context.get('parameters', {}).get('token', None)
           
            print("request_id", request_id)
            dialogflow_params = request_data.get('queryResult', {})
            
            #assignment_id = int(dialogflow_params.get('parameters', {}).get('assignmentid', ''))
            assignment_id = str(1040)

            print( request_id, assignment_id)

            external_api_data = {
               
                "requestid": request_id,
                "assignmentid":  assignment_id 
            }

            print("external_api_data", external_api_data)

            external_api_url = 'http://150.242.13.125:9092/BookingDetails_bot/'
            if token is None:
                response_data = {'fulfillmentText': f'Please Say Hello to Login'}
                self.logger.info(response_data)
                return response_data

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            }
            external_api_response = requests.get(external_api_url, json=external_api_data, headers=headers, verify=False)
            
            if external_api_response.status_code == 200:
                external_api_data = external_api_response.json()
                print(external_api_data)

                bookings = external_api_data.get('data', [])

                booking_texts = []
                for i, booking in enumerate(bookings):
                    booking_text = (
                        f"Booking {i + 1}: "
                        f"Request ID: {booking.get('requestid', 'Unknown')}\n "
                        f"Assignment id: {booking.get('assignmentid', 'Unknown')}\n "
                        f"Cost Price: {booking.get('costprice', 'Unknown')}\n "
                        f"Conformation no.: {booking.get('confno', 'Unknown')}\n"
                        f"Transfer No: {booking.get('transfertype', 'Unknown')}\n "
                        f"Status: {booking.get('assign_status', 'Unknown')}\n "
                        f"Override cost: {booking.get('overridecost', 'Unknown')}\n "
                        f"Total salevalue: {booking.get('totalsalevalue', 'Unknown')}\n"
                        f"Driver name: {booking.get('DriverName', 'Unknown')}\n"
                        #f"Driver tel: {booking.get('drivertel1', 'Unknown')}\n"
                        f"Start time: {booking.get('starttime', 'Unknown')}\n"
                        f"Endtime: {booking.get('endtime', 'Unknown')}\n"
                        f"Remarks: {booking.get('remarks', 'Unknown')}\n"
                        f"Complimentary from supplier: {booking.get('complimentaryfromsupplier', 'Unknown')}\n"
                        f"Parking fee: {booking.get('parkingfee', 'Unknown')}\n"
                        f"Total cost price: {booking.get('totalcostprice', 'Unknown')}\n"
                        #f"ServiceType: {booking.get('ServiceType', 'Unknown')}\n"
                    )
                    booking_texts.append(booking_text)

                response_text = '\n'.join(booking_texts)

                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [response_text]}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Edit'},
                                                        {'text': 'Try Another Request ID', 'intent': 'bookingTransfer'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                ],
                                'outputContexts': [
                                    {
                                        "name": f"{request_data['session']}/contexts/bookingdetails",
                                        "lifespanCount": 5
                                        ,
                                        "parameters": {
                                            "request_id": request_id,
                                            "assignment_id": assignment_id,
                                            "booking_details": {
                                                "request_id": request_id,
                                                "assignment_id": assignment_id,
                                                "cost_price": booking.get('costprice', 'Unknown'),
                                                "transfer_type": booking.get('transfertype', 'Unknown'),
                                                "confirmation_no": booking.get('confno', 'Unknown'),
                                                "status": booking.get('assign_status', 'Unknown'),
                                                "override_cost": booking.get('overridecost', 'Unknown'),
                                                "total_sale_value": booking.get('totalsalevalue', 'Unknown'),
                                                "driver_name": booking.get('DriverName', 'Unknown'),
                                                "start_time": booking.get('starttime', 'Unknown'),
                                                "end_time": booking.get('endtime', 'Unknown'),
                                                "remarks": booking.get('remarks', 'Unknown'),
                                                "complimentary_from_supplier": booking.get('complimentaryfromsupplier', 'Unknown'),
                                                "parking_fee": booking.get('parkingfee', 'Unknown'),
                                                "total_cost_price": booking.get('totalcostprice', 'Unknown')
                                               
                                            }
                                        }
                                    }
                                ]
                            }

                self.logger.info(f"Successful data Fetched {request_id} - {response_data}")
                return response_data

        

            else:
                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [  f'No Bookings available on this request_id. Status code: {external_api_response.status_code}']}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Try Another Booking Request date','intent': 'BookingTransferdate'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                                        ]
                                }
                self.logger.info(f"No Bookings available {request_id} - {response_data}")
                return response_data

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch: {str(e)}")
            return response_data
    
    
    
    def handle_cost_price_intent(self, request_data):
        try:
            output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
            print("Output Contexts:", output_contexts)
            dialogflow_params = request_data.get('queryResult', {})
            
            # Extracting token from the 'token-context' context
            token_context = next(
                (context for context in output_contexts if 'token-context' in context.get('name', '')),
                {}
            )
            token = token_context.get('parameters', {}).get('token', None)
            print("TOKEN cost:", token)

            # Extracting request_id from the 'request_id' context
            request_id_context = next(
                (context for context in output_contexts if 'request_id' in context.get('name', '')),
                {}
            )
            requestids = request_id_context.get('parameters', {}).get('request_id', None)
            print("request_id_context:", request_id_context)
            print('requestids:', requestids)

            # Extracting booking details from the 'bookingdetails' context
            bookingdetails_context = next(
                (context for context in output_contexts if context.get('name', '').endswith('bookingdetails')),
                {}
            )
            booking_details = bookingdetails_context.get('parameters', {}).get('booking_details', {})
            
            # Extracting individual booking details
            transfer_type = booking_details.get('transfer_type', None)
            confirmation_no = booking_details.get('confirmation_no', None)
            status = booking_details.get('status', None)
            override_cost = float(booking_details.get('override_cost', 0))
            total_sale_value = float(booking_details.get('total_sale_value', None))
            driver_name = booking_details.get('driver_name', None)
            start_time = booking_details.get('start_time', None)
            end_time = booking_details.get('end_time', None)
            remarks = booking_details.get('remarks', None)
            complimentary_from_supplier = booking_details.get('complimentary_from_supplier', None)
            parking_fee = booking_details.get('parking_fee', None)
            total_cost_price = float(booking_details.get('total_cost_price', None))
            assignment_id = str(1040)

            # Convert costprice to float
            costprice = float(dialogflow_params.get('parameters', {}).get('costprice', 0))
            mode = "Edit"

            external_api_url = 'http://150.242.13.125:9092/costprice/' 
            
            # Construct external API data
            external_api_data = {'requestids': requestids, 'transfertype': transfer_type, 'assigntype': 'ARRIVAL', 'partycode': 'OWN TRANSPORT', 'remarks': remarks, 'confno': confirmation_no, 'assign_status': status, 'costprice': costprice, 'overridecost': override_cost, 'totalsalevalue': total_sale_value, 'vehicleno': '', 'drivercode': '', 'drivername': driver_name, 'drivertel1': '', 'drivertel2': '', 'starttime': start_time, 'endtime': end_time, 'complimentaryfromsupplier': complimentary_from_supplier, 'vehiclemaxpax': '0', 'overridemaxpax': '0', 'adddate': '', 'adduser': '', 'moddate': '2023/11/27', 'moduser': 'Sys Admin', 'cartype': '000001', 'sectorgroupcode': '000001', 'mode': mode, 'assignmentid': assignment_id, 'ServiceType': 'TRANSFER', 'salevalue': 30.000, 'parkingfee': parking_fee, 'totalcostprice': total_cost_price}

            print('external_api_data:', external_api_data)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            }

            external_api_response = requests.put(external_api_url, json=external_api_data, headers=headers, verify=False)

            print(external_api_response)
            if external_api_response.status_code == 200:
                # Create the final Dialogflow response
                response_data = {
                    'fulfillmentMessages': [
                        {'text': {'text': ["Data Update Successfully"]}},
                        {
                            'payload': {
                                'richContent': [
                                    [{'type': 'chips', 'options': [
                                        {'text': 'View'},
                                        {'text': 'Try Another Request ID', 'intent': 'bookingtransfer'}
                                    ]}]
                                ]
                            }
                        }
                    ]
                }
                self.logger.info(f"Data Updated Successfully {requestids} {response_data}")
                return response_data
        
    

            else:
                output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
                print("Output Contexts:", output_contexts)
                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [f'Please Try Again. Status code: {external_api_response.status_code}']}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Booking Request'},
                                                        {'text': 'Try Again-Cost Price','intent': 'costprice'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                                        ]
                                }
                self.logger.info(f"Data  Not Updated {requestids} {response_data}")
                return (response_data)

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return (response_data)
        

    def handle_transfer_type_intent(self, request_data):
        try:
            output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
            print("Output Contexts:", output_contexts)
            dialogflow_params = request_data.get('queryResult', {})
            
            # Extracting token from the 'token-context' context
            token_context = next(
                (context for context in output_contexts if 'token-context' in context.get('name', '')),
                {}
            )
            token = token_context.get('parameters', {}).get('token', None)
            print("TOKEN cost:", token)

            # Extracting request_id from the 'request_id' context
            request_id_context = next(
                (context for context in output_contexts if 'request_id' in context.get('name', '')),
                {}
            )
            requestids = request_id_context.get('parameters', {}).get('request_id', None)
            print("request_id_context:", request_id_context)
            print('requestids:', requestids)

            # Extracting booking details from the 'bookingdetails' context
            bookingdetails_context = next(
                (context for context in output_contexts if context.get('name', '').endswith('bookingdetails')),
                {}
            )
            booking_details = bookingdetails_context.get('parameters', {}).get('booking_details', {})
            
            # Extracting individual booking details
            costprice = str(booking_details.get('cost_price', None))
            confirmation_no = booking_details.get('confirmation_no', None)
            status = booking_details.get('status', None)
            override_cost = float(booking_details.get('override_cost', 0))
            total_sale_value = float(booking_details.get('total_sale_value', None))
            driver_name = booking_details.get('driver_name', None)
            start_time = booking_details.get('start_time', None)
            end_time = booking_details.get('end_time', None)
            remarks = booking_details.get('remarks', None)
            complimentary_from_supplier = booking_details.get('complimentary_from_supplier', None)
            parking_fee = float(booking_details.get('parking_fee', None))
            total_cost_price = float(booking_details.get('total_cost_price', None))
            assignment_id = str(1040)
  
            transfertype = str(dialogflow_params.get('parameters', {}).get('transfertype', 0))
            mode = "Edit"

            external_api_url = 'http://150.242.13.125:9092/costprice/' 

            external_api_data = {'requestids': requestids, 'transfertype': transfertype, 'assigntype': 'ARRIVAL', 'partycode': 'OWN TRANSPORT', 'remarks': remarks, 'confno': confirmation_no, 'assign_status': status, 'costprice': costprice, 'overridecost': override_cost, 'totalsalevalue': total_sale_value, 'vehicleno': '', 'drivercode': '', 'drivername': driver_name, 'drivertel1': '', 'drivertel2': '', 'starttime': start_time, 'endtime': end_time, 'complimentaryfromsupplier': complimentary_from_supplier, 'vehiclemaxpax': '0', 'overridemaxpax': '0', 'adddate': '', 'adduser': '', 'moddate': '2023/11/27', 'moduser': 'Sys Admin', 'cartype': '000001', 'sectorgroupcode': '000001','costcurrcode':'', 'mode': mode, 'assignmentid': assignment_id, 'ServiceType': 'TRANSFER', 'salevalue': 30.000, 'parkingfee': parking_fee, 'totalcostprice': total_cost_price}

            print('external_api_data', external_api_data)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            }

            external_api_response = requests.put(external_api_url, json=external_api_data, headers=headers, verify=False)
            print(external_api_response)
            if external_api_response.status_code == 200:
                # Create the final Dialogflow response
                response_data = {
                    'fulfillmentMessages': [
                        {'text': {'text': ["Data Update Successfully"]}},
                        {
                            'payload': {
                                'richContent': [
                                    [{'type': 'chips', 'options': [
                                        {'text': 'View'},
                                        {'text': 'Try Another Request ID', 'intent': 'bookingtransfer'}
                                    ]}]
                                ]
                            }
                        }
                    ]
                }
                self.logger.info(f"Data Updated Successfully {requestids} {response_data}")
                return response_data


            else:
                output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
                print("Output Contexts:", output_contexts)
                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [f'Please Try Again. Status code: {external_api_response.status_code}']}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Main Menu'},
                                                        {'text': 'Try Again-Cost Price','intent': 'costprice'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                                        ]
                                }
                self.logger.info(f"Data  Not Updated {requestids} {response_data}")
                return (response_data)

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return (response_data)


    def handle_conf_no_intent(self, request_data):
        try:
            output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
            print("Output Contexts:", output_contexts)
            dialogflow_params = request_data.get('queryResult', {})
            
            # Extracting token from the 'token-context' context
            token_context = next(
                (context for context in output_contexts if 'token-context' in context.get('name', '')),
                {}
            )
            token = token_context.get('parameters', {}).get('token', None)
            print("TOKEN cost:", token)

            # Extracting request_id from the 'request_id' context
            request_id_context = next(
                (context for context in output_contexts if 'request_id' in context.get('name', '')),
                {}
            )
            requestids = request_id_context.get('parameters', {}).get('request_id', None)
            print("request_id_context:", request_id_context)
            print('requestids:', requestids)

            # Extracting booking details from the 'bookingdetails' context
            bookingdetails_context = next(
                (context for context in output_contexts if context.get('name', '').endswith('bookingdetails')),
                {}
            )
            booking_details = bookingdetails_context.get('parameters', {}).get('booking_details', {})
            
            # Extracting individual booking details
            costprice = str(booking_details.get('cost_price', None))
            transfer_type = booking_details.get('transfer_type', None)
            status = booking_details.get('status', None)
            override_cost = float(booking_details.get('override_cost', 0))
            total_sale_value = float(booking_details.get('total_sale_value', None))
            driver_name = booking_details.get('driver_name', None)
            start_time = booking_details.get('start_time', None)
            end_time = booking_details.get('end_time', None)
            remarks = booking_details.get('remarks', None)
            complimentary_from_supplier = booking_details.get('complimentary_from_supplier', None)
            parking_fee = float(booking_details.get('parking_fee', None))
            total_cost_price = float(booking_details.get('total_cost_price', None))
            assignment_id = str(1040)
    
            confno = str(dialogflow_params.get('parameters', {}).get('confno', 0))
            mode = "Edit"

            external_api_url = 'http://150.242.13.125:9092/costprice/' 
            external_api_data = {'requestids': requestids, 'transfertype': transfer_type, 'assigntype': 'ARRIVAL', 'partycode': 'OWN TRANSPORT', 'remarks': remarks, 'confno': confno, 'assign_status': status, 'costprice': costprice, 'overridecost': override_cost, 'totalsalevalue': total_sale_value, 'vehicleno': '', 'drivercode': '', 'drivername': driver_name, 'drivertel1': '', 'drivertel2': '', 'starttime': start_time, 'endtime': end_time, 'complimentaryfromsupplier': complimentary_from_supplier, 'vehiclemaxpax': '0', 'overridemaxpax': '0', 'adddate': '', 'adduser': '', 'moddate': '2023/11/27', 'moduser': 'Sys Admin', 'cartype': '000001', 'sectorgroupcode': '000001','costcurrcode':'', 'mode': mode, 'assignmentid': assignment_id, 'ServiceType': 'TRANSFER', 'salevalue': 30.000, 'parkingfee': parking_fee, 'totalcostprice': total_cost_price} 
            print('external_api_data', external_api_data)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            }

            external_api_response = requests.put(external_api_url, json=external_api_data, headers=headers, verify=False)
            print(external_api_response)
            if external_api_response.status_code == 200:
                # Create the final Dialogflow response
                response_data = {
                    'fulfillmentMessages': [
                        {'text': {'text': ["Data Update Successfully"]}},
                        {
                            'payload': {
                                'richContent': [
                                    [{'type': 'chips', 'options': [
                                        {'text': 'View'},
                                        {'text': 'Try Another Request ID', 'intent': 'bookingtransfer'}
                                    ]}]
                                ]
                            }
                        }
                    ]
                }
                self.logger.info(f"Data Updated Successfully {requestids} {response_data}")
                return response_data


            else:
                output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
                print("Output Contexts:", output_contexts)
                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [f'Please Try Again. Status code: {external_api_response.status_code}']}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Main Menu'},
                                                        {'text': 'Try Again-Cost Price','intent': 'costprice'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                                        ]
                                }
                self.logger.info(f"Data  Not Updated {requestids} {response_data}")
                return (response_data)

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return (response_data)

    
    def handle_status_intent(self, request_data):
        try:
            output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
            print("Output Contexts:", output_contexts)
            dialogflow_params = request_data.get('queryResult', {})
            
            # Extracting token from the 'token-context' context
            token_context = next(
                (context for context in output_contexts if 'token-context' in context.get('name', '')),
                {}
            )
            token = token_context.get('parameters', {}).get('token', None)
            print("TOKEN cost:", token)

            # Extracting request_id from the 'request_id' context
            request_id_context = next(
                (context for context in output_contexts if 'request_id' in context.get('name', '')),
                {}
            )
            requestids = request_id_context.get('parameters', {}).get('request_id', None)
            print("request_id_context:", request_id_context)
            print('requestids:', requestids)

            # Extracting booking details from the 'bookingdetails' context
            bookingdetails_context = next(
                (context for context in output_contexts if context.get('name', '').endswith('bookingdetails')),
                {}
            )
            booking_details = bookingdetails_context.get('parameters', {}).get('booking_details', {})
            
            # Extracting individual booking details
            costprice = str(booking_details.get('cost_price', None))
            transfer_type = booking_details.get('transfer_type', None)
            confirmation_no = booking_details.get('confirmation_no', None)
            override_cost = float(booking_details.get('override_cost', 0))
            total_sale_value = float(booking_details.get('total_sale_value', None))
            driver_name = booking_details.get('driver_name', None)
            start_time = booking_details.get('start_time', None)
            end_time = booking_details.get('end_time', None)
            remarks = booking_details.get('remarks', None)
            complimentary_from_supplier = booking_details.get('complimentary_from_supplier', None)
            parking_fee = float(booking_details.get('parking_fee', None))
            total_cost_price = float(booking_details.get('total_cost_price', None))
            assignment_id = str(1040)
            assign_status = str(dialogflow_params.get('parameters', {}).get('status', 0))
            mode = "Edit"

            external_api_url = 'http://150.242.13.125:9092/costprice/' 
            external_api_data = {'requestids': requestids, 'transfertype': transfer_type, 'assigntype': 'ARRIVAL', 'partycode': 'OWN TRANSPORT', 'remarks': remarks, 'confno': confirmation_no, 'assign_status': assign_status, 'costprice': costprice, 'overridecost': override_cost, 'totalsalevalue': total_sale_value, 'vehicleno': '', 'drivercode': '', 'drivername': driver_name, 'drivertel1': '', 'drivertel2': '', 'starttime': start_time, 'endtime': end_time, 'complimentaryfromsupplier': complimentary_from_supplier, 'vehiclemaxpax': '0', 'overridemaxpax': '0', 'adddate': '', 'adduser': '', 'moddate': '2023/11/27', 'moduser': 'Sys Admin', 'cartype': '000001', 'sectorgroupcode': '000001','costcurrcode':'', 'mode': mode, 'assignmentid': assignment_id, 'ServiceType': 'TRANSFER', 'salevalue': 30.000, 'parkingfee': parking_fee, 'totalcostprice': total_cost_price}  
            print('external_api_data', external_api_data)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            }

            external_api_response = requests.put(external_api_url, json=external_api_data, headers=headers, verify=False)
            print(external_api_response)
            if external_api_response.status_code == 200:
                # Create the final Dialogflow response
                response_data = {
                    'fulfillmentMessages': [
                        {'text': {'text': ["Data Update Successfully"]}},
                        {
                            'payload': {
                                'richContent': [
                                    [{'type': 'chips', 'options': [
                                        {'text': 'View'},
                                        {'text': 'Try Another Request ID', 'intent': 'bookingtransfer'}
                                    ]}]
                                ]
                            }
                        }
                    ]
                }
                self.logger.info(f"Data Updated Successfully {requestids} {response_data}")
                return response_data


            else:
                output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
                print("Output Contexts:", output_contexts)
                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [f'Please Try Again. Status code: {external_api_response.status_code}']}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Main Menu'},
                                                        {'text': 'Try Again-Cost Price','intent': 'costprice'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                                        ]
                                }
                self.logger.info(f"Data  Not Updated {requestids} {response_data}")
                return (response_data)

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return (response_data)


    def handle_driver_name_intent(self, request_data):
        try:
            output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
            print("Output Contexts:", output_contexts)
            dialogflow_params = request_data.get('queryResult', {})
            
            # Extracting token from the 'token-context' context
            token_context = next(
                (context for context in output_contexts if 'token-context' in context.get('name', '')),
                {}
            )
            token = token_context.get('parameters', {}).get('token', None)
            print("TOKEN cost:", token)

            # Extracting request_id from the 'request_id' context
            request_id_context = next(
                (context for context in output_contexts if 'request_id' in context.get('name', '')),
                {}
            )
            requestids = request_id_context.get('parameters', {}).get('request_id', None)
            print("request_id_context:", request_id_context)
            print('requestids:', requestids)

            # Extracting booking details from the 'bookingdetails' context
            bookingdetails_context = next(
                (context for context in output_contexts if context.get('name', '').endswith('bookingdetails')),
                {}
            )
            booking_details = bookingdetails_context.get('parameters', {}).get('booking_details', {})
            
            # Extracting individual booking details
            costprice = str(booking_details.get('cost_price', None))
            transfer_type = booking_details.get('transfer_type', None)
            confirmation_no = booking_details.get('confirmation_no', None)
            override_cost = float(booking_details.get('override_cost', 0))
            total_sale_value = float(booking_details.get('total_sale_value', None))
            status = booking_details.get('status', None)
            start_time = booking_details.get('start_time', None)
            end_time = booking_details.get('end_time', None)
            remarks = booking_details.get('remarks', None)
            complimentary_from_supplier = booking_details.get('complimentary_from_supplier', None)
            parking_fee = float(booking_details.get('parking_fee', None))
            total_cost_price = float(booking_details.get('total_cost_price', None))
            assignment_id = str(1040) 
            drivername = str(dialogflow_params.get('parameters', {}).get('drivername', 0))
            mode = "Edit"

            external_api_url = 'http://150.242.13.125:9092/costprice/' 
            external_api_data = {'requestids': requestids, 'transfertype': transfer_type, 'assigntype': 'ARRIVAL', 'partycode': 'OWN TRANSPORT', 'remarks': remarks, 'confno': confirmation_no, 'assign_status': status, 'costprice': costprice, 'overridecost': override_cost, 'totalsalevalue': total_sale_value, 'vehicleno': '', 'drivercode': '', 'drivername': drivername, 'drivertel1': '', 'drivertel2': '', 'starttime': start_time, 'endtime': end_time, 'complimentaryfromsupplier': complimentary_from_supplier, 'vehiclemaxpax': '0', 'overridemaxpax': '0', 'adddate': '', 'adduser': '', 'moddate': '2023/11/27', 'moduser': 'Sys Admin', 'cartype': '000001', 'sectorgroupcode': '000001','costcurrcode':'', 'mode': mode, 'assignmentid': assignment_id, 'ServiceType': 'TRANSFER', 'salevalue': 30.000, 'parkingfee': parking_fee, 'totalcostprice': total_cost_price}   
            print('external_api_data', external_api_data)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            }

            external_api_response = requests.put(external_api_url, json=external_api_data, headers=headers, verify=False)
            print(external_api_response)
            if external_api_response.status_code == 200:
                # Create the final Dialogflow response
                response_data = {
                    'fulfillmentMessages': [
                        {'text': {'text': ["Data Update Successfully"]}},
                        {
                            'payload': {
                                'richContent': [
                                    [{'type': 'chips', 'options': [
                                        {'text': 'View'},
                                        {'text': 'Try Another Request ID', 'intent': 'bookingtransfer'}
                                    ]}]
                                ]
                            }
                        }
                    ]
                }
                self.logger.info(f"Data Updated Successfully {requestids} {response_data}")
                return response_data


            else:
                output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
                print("Output Contexts:", output_contexts)
                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [f'Please Try Again. Status code: {external_api_response.status_code}']}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Main Menu'},
                                                        {'text': 'Try Again-Cost Price','intent': 'costprice'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                                        ]
                                }
                self.logger.info(f"Data  Not Updated {requestids} {response_data}")
                return (response_data)

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return (response_data)


    def handle_override_cost_intent(self, request_data):
        try:
            output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
            print("Output Contexts:", output_contexts)
            dialogflow_params = request_data.get('queryResult', {})
            
            # Extracting token from the 'token-context' context
            token_context = next(
                (context for context in output_contexts if 'token-context' in context.get('name', '')),
                {}
            )
            token = token_context.get('parameters', {}).get('token', None)
            print("TOKEN cost:", token)

            # Extracting request_id from the 'request_id' context
            request_id_context = next(
                (context for context in output_contexts if 'request_id' in context.get('name', '')),
                {}
            )
            requestids = request_id_context.get('parameters', {}).get('request_id', None)
            print("request_id_context:", request_id_context)
            print('requestids:', requestids)

            # Extracting booking details from the 'bookingdetails' context
            bookingdetails_context = next(
                (context for context in output_contexts if context.get('name', '').endswith('bookingdetails')),
                {}
            )
            booking_details = bookingdetails_context.get('parameters', {}).get('booking_details', {})
            
            # Extracting individual booking details
            costprice = str(booking_details.get('cost_price', None))
            transfer_type = booking_details.get('transfer_type', None)
            confirmation_no = booking_details.get('confirmation_no', None)
            driver_name = (booking_details.get('driver_name', 0))
            total_sale_value = float(booking_details.get('total_sale_value', None))
            status = booking_details.get('status', None)
            start_time = booking_details.get('start_time', None)
            end_time = booking_details.get('end_time', None)
            remarks = booking_details.get('remarks', None)
            complimentary_from_supplier = booking_details.get('complimentary_from_supplier', None)
            parking_fee = float(booking_details.get('parking_fee', None))
            total_cost_price = float(booking_details.get('total_cost_price', None))
            assignment_id = str(1040)  
            overridecost = float(dialogflow_params.get('parameters', {}).get('overridecost', 0))
            mode = "Edit"

            external_api_url = 'http://150.242.13.125:9092/costprice/' 
            external_api_data = {'requestids': requestids, 'transfertype': transfer_type, 'assigntype': 'ARRIVAL', 'partycode': 'OWN TRANSPORT', 'remarks': remarks, 'confno': confirmation_no, 'assign_status': status, 'costprice': costprice, 'overridecost': overridecost, 'totalsalevalue': total_sale_value, 'vehicleno': '', 'drivercode': '', 'drivername': driver_name, 'drivertel1': '', 'drivertel2': '', 'starttime': start_time, 'endtime': end_time, 'complimentaryfromsupplier': complimentary_from_supplier, 'vehiclemaxpax': '0', 'overridemaxpax': '0', 'adddate': '', 'adduser': '', 'moddate': '2023/11/27', 'moduser': 'Sys Admin', 'cartype': '000001', 'sectorgroupcode': '000001','costcurrcode':'', 'mode': mode, 'assignmentid': assignment_id, 'ServiceType': 'TRANSFER', 'salevalue': 30.000, 'parkingfee': parking_fee, 'totalcostprice': total_cost_price}  
            print('external_api_data', external_api_data)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            }

            external_api_response = requests.put(external_api_url, json=external_api_data, headers=headers, verify=False)
            print(external_api_response)
            if external_api_response.status_code == 200:
                # Create the final Dialogflow response
                response_data = {
                    'fulfillmentMessages': [
                        {'text': {'text': ["Data Update Successfully"]}},
                        {
                            'payload': {
                                'richContent': [
                                    [{'type': 'chips', 'options': [
                                        {'text': 'View'},
                                        {'text': 'Try Another Request ID', 'intent': 'bookingtransfer'}
                                    ]}]
                                ]
                            }
                        }
                    ]
                }
                self.logger.info(f"Data Updated Successfully {requestids} {response_data}")
                return response_data


            else:
                output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
                print("Output Contexts:", output_contexts)
                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [f'Please Try Again. Status code: {external_api_response.status_code}']}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Main Menu'},
                                                        {'text': 'Try Again-Cost Price','intent': 'costprice'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                                        ]
                                }
                self.logger.info(f"Data  Not Updated {requestids} {response_data}")
                return (response_data)

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return (response_data)
        
    

    def handle_start_time_intent(self, request_data):
        try:
            output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
            print("Output Contexts:", output_contexts)
            dialogflow_params = request_data.get('queryResult', {})
            
            # Extracting token from the 'token-context' context
            token_context = next(
                (context for context in output_contexts if 'token-context' in context.get('name', '')),
                {}
            )
            token = token_context.get('parameters', {}).get('token', None)
            print("TOKEN cost:", token)

            # Extracting request_id from the 'request_id' context
            request_id_context = next(
                (context for context in output_contexts if 'request_id' in context.get('name', '')),
                {}
            )
            requestids = request_id_context.get('parameters', {}).get('request_id', None)
            print("request_id_context:", request_id_context)
            print('requestids:', requestids)

            # Extracting booking details from the 'bookingdetails' context
            bookingdetails_context = next(
                (context for context in output_contexts if context.get('name', '').endswith('bookingdetails')),
                {}
            )
            booking_details = bookingdetails_context.get('parameters', {}).get('booking_details', {})
            
            # Extracting individual booking details
            costprice = str(booking_details.get('cost_price', None))
            transfer_type = booking_details.get('transfer_type', None)
            confirmation_no = booking_details.get('confirmation_no', None)
            driver_name = (booking_details.get('driver_name', 0))
            total_sale_value = float(booking_details.get('total_sale_value', None))
            status = booking_details.get('status', None)
            override_cost = float(booking_details.get('override_cost', None))
            end_time = booking_details.get('end_time', None)
            remarks = booking_details.get('remarks', None)
            complimentary_from_supplier = booking_details.get('complimentary_from_supplier', None)
            parking_fee = float(booking_details.get('parking_fee', None))
            total_cost_price = float(booking_details.get('total_cost_price', None))
            assignment_id = str(1040) 
            starttime_str = dialogflow_params.get('parameters', {}).get('starttime', '2023-11-15T12:00:00+06:00')
            # Parse ISO 8601 formatted string
            starttime = datetime.fromisoformat(starttime_str)
            # Convert datetime object to string
            starttime_str = starttime.strftime('%Y-%m-%d %H:%M:%S')
            mode = "Edit"
            
            external_api_url = 'http://150.242.13.125:9092/costprice/' 
            external_api_data = {'requestids': requestids, 'transfertype': transfer_type, 'assigntype': 'ARRIVAL', 'partycode': 'OWN TRANSPORT', 'remarks': remarks, 'confno': confirmation_no, 'assign_status': status, 'costprice': costprice, 'overridecost': override_cost, 'totalsalevalue': total_sale_value, 'vehicleno': '', 'drivercode': '', 'drivername': driver_name, 'drivertel1': '', 'drivertel2': '', 'starttime': starttime_str, 'endtime': end_time, 'complimentaryfromsupplier': complimentary_from_supplier, 'vehiclemaxpax': '0', 'overridemaxpax': '0', 'adddate': '', 'adduser': '', 'moddate': '2023/11/27', 'moduser': 'Sys Admin', 'cartype': '000001', 'sectorgroupcode': '000001','costcurrcode':'', 'mode': mode, 'assignmentid': assignment_id, 'ServiceType': 'TRANSFER', 'salevalue': 30.000, 'parkingfee': parking_fee, 'totalcostprice': total_cost_price}  

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            }

            external_api_response = requests.put(external_api_url, json=external_api_data, headers=headers, verify=False)
            print(external_api_response)
            if external_api_response.status_code == 200:
                # Create the final Dialogflow response
                response_data = {
                    'fulfillmentMessages': [
                        {'text': {'text': ["Data Update Successfully"]}},
                        {
                            'payload': {
                                'richContent': [
                                    [{'type': 'chips', 'options': [
                                        {'text': 'View'},
                                        {'text': 'Try Another Request ID', 'intent': 'bookingtransfer'}
                                    ]}]
                                ]
                            }
                        }
                    ]
                }
                self.logger.info(f"Data Updated Successfully {requestids} {response_data}")
                return response_data


            else:
                output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
                print("Output Contexts:", output_contexts)
                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [f'Please Try Again. Status code: {external_api_response.status_code}']}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Main Menu'},
                                                        {'text': 'Try Again-Cost Price','intent': 'costprice'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                                        ]
                                }
                self.logger.info(f"Data  Not Updated {requestids} {response_data}")
                return (response_data)

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return (response_data)


    def handle_end_time_intent(self, request_data):
        try:
            output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
            print("Output Contexts:", output_contexts)
            dialogflow_params = request_data.get('queryResult', {})
            
            # Extracting token from the 'token-context' context
            token_context = next(
                (context for context in output_contexts if 'token-context' in context.get('name', '')),
                {}
            )
            token = token_context.get('parameters', {}).get('token', None)
            print("TOKEN cost:", token)

            # Extracting request_id from the 'request_id' context
            request_id_context = next(
                (context for context in output_contexts if 'request_id' in context.get('name', '')),
                {}
            )
            requestids = request_id_context.get('parameters', {}).get('request_id', None)
            print("request_id_context:", request_id_context)
            print('requestids:', requestids)

            # Extracting booking details from the 'bookingdetails' context
            bookingdetails_context = next(
                (context for context in output_contexts if context.get('name', '').endswith('bookingdetails')),
                {}
            )
            booking_details = bookingdetails_context.get('parameters', {}).get('booking_details', {})
            
            # Extracting individual booking details
            costprice = str(booking_details.get('cost_price', None))
            transfer_type = booking_details.get('transfer_type', None)
            confirmation_no = booking_details.get('confirmation_no', None)
            driver_name = (booking_details.get('driver_name', 0))
            total_sale_value = float(booking_details.get('total_sale_value', None))
            status = booking_details.get('status', None)
            override_cost = float(booking_details.get('override_cost', None))
            start_time = booking_details.get('start_time', None)
            remarks = booking_details.get('remarks', None)
            complimentary_from_supplier = booking_details.get('complimentary_from_supplier', None)
            parking_fee = float(booking_details.get('parking_fee', None))
            total_cost_price = float(booking_details.get('total_cost_price', None))
            assignment_id = str(1040)
            endtime_str = dialogflow_params.get('parameters', {}).get('endtime', '2023-11-15T12:00:00+06:00')
            # Parse ISO 8601 formatted string
            endtime = datetime.fromisoformat(endtime_str)
            # Convert datetime object to string
            endtime_str = endtime.strftime('%Y-%m-%d %H:%M:%S')
            mode = "Edit"
            
            external_api_url = 'http://150.242.13.125:9092/costprice/' 
            external_api_data = {'requestids': requestids, 'transfertype': transfer_type, 'assigntype': 'ARRIVAL', 'partycode': 'OWN TRANSPORT', 'remarks': remarks, 'confno': confirmation_no, 'assign_status': status, 'costprice': costprice, 'overridecost': override_cost, 'totalsalevalue': total_sale_value, 'vehicleno': '', 'drivercode': '', 'drivername': driver_name, 'drivertel1': '', 'drivertel2': '', 'starttime': start_time, 'endtime': endtime_str, 'complimentaryfromsupplier': complimentary_from_supplier, 'vehiclemaxpax': '0', 'overridemaxpax': '0', 'adddate': '', 'adduser': '', 'moddate': '2023/11/27', 'moduser': 'Sys Admin', 'cartype': '000001', 'sectorgroupcode': '000001','costcurrcode':'', 'mode': mode, 'assignmentid': assignment_id, 'ServiceType': 'TRANSFER', 'salevalue': 30.000, 'parkingfee': parking_fee, 'totalcostprice': total_cost_price}   
            print('external_api_data', external_api_data)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            }

            external_api_response = requests.put(external_api_url, json=external_api_data, headers=headers, verify=False)
            print(external_api_response)
            if external_api_response.status_code == 200:
                # Create the final Dialogflow response
                response_data = {
                    'fulfillmentMessages': [
                        {'text': {'text': ["Data Update Successfully"]}},
                        {
                            'payload': {
                                'richContent': [
                                    [{'type': 'chips', 'options': [
                                        {'text': 'View'},
                                        {'text': 'Try Another Request ID', 'intent': 'bookingtransfer'}
                                    ]}]
                                ]
                            }
                        }
                    ]
                }
                self.logger.info(f"Data Updated Successfully {requestids} {response_data}")
                return response_data


            else:
                output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
                print("Output Contexts:", output_contexts)
                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [f'Please Try Again. Status code: {external_api_response.status_code}']}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Main Menu'},
                                                        {'text': 'Try Again-Cost Price','intent': 'costprice'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                                        ]
                                }
                self.logger.info(f"Data  Not Updated {requestids} {response_data}")
                return (response_data)

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return (response_data)


    def handle_remark_intent(self, request_data):
        try:
            output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
            print("Output Contexts:", output_contexts)
            dialogflow_params = request_data.get('queryResult', {})
            
            # Extracting token from the 'token-context' context
            token_context = next(
                (context for context in output_contexts if 'token-context' in context.get('name', '')),
                {}
            )
            token = token_context.get('parameters', {}).get('token', None)
            print("TOKEN cost:", token)

            # Extracting request_id from the 'request_id' context
            request_id_context = next(
                (context for context in output_contexts if 'request_id' in context.get('name', '')),
                {}
            )
            requestids = request_id_context.get('parameters', {}).get('request_id', None)
            print("request_id_context:", request_id_context)
            print('requestids:', requestids)

            # Extracting booking details from the 'bookingdetails' context
            bookingdetails_context = next(
                (context for context in output_contexts if context.get('name', '').endswith('bookingdetails')),
                {}
            )
            booking_details = bookingdetails_context.get('parameters', {}).get('booking_details', {})
            
            # Extracting individual booking details
            costprice = str(booking_details.get('cost_price', None))
            transfer_type = booking_details.get('transfer_type', None)
            confirmation_no = booking_details.get('confirmation_no', None)
            driver_name = (booking_details.get('driver_name', 0))
            total_sale_value = float(booking_details.get('total_sale_value', None))
            status = booking_details.get('status', None)
            override_cost = float(booking_details.get('override_cost', None))
            start_time = booking_details.get('start_time', None)
            end_time = booking_details.get('end_time', None)
            complimentary_from_supplier = booking_details.get('complimentary_from_supplier', None)
            parking_fee = float(booking_details.get('parking_fee', None))
            total_cost_price = float(booking_details.get('total_cost_price', None))
            assignment_id = str(1040) 
            remark = str(dialogflow_params.get('parameters', {}).get('remark', 0))
            mode = "Edit"

            external_api_url = 'http://150.242.13.125:9092/costprice/' 
            external_api_data = {'requestids': requestids, 'transfertype': transfer_type, 'assigntype': 'ARRIVAL', 'partycode': 'OWN TRANSPORT', 'remarks': remark, 'confno': confirmation_no, 'assign_status': status, 'costprice': costprice, 'overridecost': override_cost, 'totalsalevalue': total_sale_value, 'vehicleno': '', 'drivercode': '', 'drivername': driver_name, 'drivertel1': '', 'drivertel2': '', 'starttime': start_time, 'endtime': end_time, 'complimentaryfromsupplier': complimentary_from_supplier, 'vehiclemaxpax': '0', 'overridemaxpax': '0', 'adddate': '', 'adduser': '', 'moddate': '2023/11/27', 'moduser': 'Sys Admin', 'cartype': '000001', 'sectorgroupcode': '000001','costcurrcode':'', 'mode': mode, 'assignmentid': assignment_id, 'ServiceType': 'TRANSFER', 'salevalue': 30.000, 'parkingfee': parking_fee, 'totalcostprice': total_cost_price}  
            print('external_api_data', external_api_data)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            }

            external_api_response = requests.put(external_api_url, json=external_api_data, headers=headers, verify=False)
            print(external_api_response)
            if external_api_response.status_code == 200:
                # Create the final Dialogflow response
                response_data = {
                    'fulfillmentMessages': [
                        {'text': {'text': ["Data Update Successfully"]}},
                        {
                            'payload': {
                                'richContent': [
                                    [{'type': 'chips', 'options': [
                                        {'text': 'View'},
                                        {'text': 'Try Another Request ID', 'intent': 'bookingtransfer'}
                                    ]}]
                                ]
                            }
                        }
                    ]
                }
                self.logger.info(f"Data Updated Successfully {requestids} {response_data}")
                return response_data


            else:
                output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
                print("Output Contexts:", output_contexts)
                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [f'Please Try Again. Status code: {external_api_response.status_code}']}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Main Menu'},
                                                        {'text': 'Try Again-Cost Price','intent': 'costprice'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                                        ]
                                }
                self.logger.info(f"Data  Not Updated {requestids} {response_data}")
                return (response_data)

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return (response_data)

    
    def handle_parking_intent(self, request_data):
        try:
            output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
            print("Output Contexts:", output_contexts)
            dialogflow_params = request_data.get('queryResult', {})
            
            # Extracting token from the 'token-context' context
            token_context = next(
                (context for context in output_contexts if 'token-context' in context.get('name', '')),
                {}
            )
            token = token_context.get('parameters', {}).get('token', None)
            print("TOKEN cost:", token)

            # Extracting request_id from the 'request_id' context
            request_id_context = next(
                (context for context in output_contexts if 'request_id' in context.get('name', '')),
                {}
            )
            requestids = request_id_context.get('parameters', {}).get('request_id', None)
            print("request_id_context:", request_id_context)
            print('requestids:', requestids)

            # Extracting booking details from the 'bookingdetails' context
            bookingdetails_context = next(
                (context for context in output_contexts if context.get('name', '').endswith('bookingdetails')),
                {}
            )
            booking_details = bookingdetails_context.get('parameters', {}).get('booking_details', {})
            
            # Extracting individual booking details
            costprice = str(booking_details.get('cost_price', None))
            transfer_type = booking_details.get('transfer_type', None)
            confirmation_no = booking_details.get('confirmation_no', None)
            driver_name = (booking_details.get('driver_name', 0))
            total_sale_value = float(booking_details.get('total_sale_value', None))
            status = booking_details.get('status', None)
            override_cost = float(booking_details.get('override_cost', None))
            start_time = booking_details.get('start_time', None)
            end_time = booking_details.get('end_time', None)
            complimentary_from_supplier = booking_details.get('complimentary_from_supplier', None)
            remarks = (booking_details.get('remarks', None))
            total_cost_price = float(booking_details.get('total_cost_price', None))
            assignment_id = str(1040) 
            parkingfee = float(dialogflow_params.get('parameters', {}).get('parkingfee', 0))
            mode = "Edit"

            external_api_url = 'http://150.242.13.125:9092/costprice/' 
            external_api_data = {'requestids': requestids, 'transfertype': transfer_type, 'assigntype': 'ARRIVAL', 'partycode': 'OWN TRANSPORT', 'remarks': remarks, 'confno': confirmation_no, 'assign_status': status, 'costprice': costprice, 'overridecost': override_cost, 'totalsalevalue': total_sale_value, 'vehicleno': '', 'drivercode': '', 'drivername': driver_name, 'drivertel1': '', 'drivertel2': '', 'starttime': start_time, 'endtime': end_time, 'complimentaryfromsupplier': complimentary_from_supplier, 'vehiclemaxpax': '0', 'overridemaxpax': '0', 'adddate': '', 'adduser': '', 'moddate': '2023/11/27', 'moduser': 'Sys Admin', 'cartype': '000001', 'sectorgroupcode': '000001','costcurrcode':'', 'mode': mode, 'assignmentid': assignment_id, 'ServiceType': 'TRANSFER', 'salevalue': 30.000, 'parkingfee': parkingfee, 'totalcostprice': total_cost_price}    
            print('external_api_data', external_api_data)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            }

            external_api_response = requests.put(external_api_url, json=external_api_data, headers=headers, verify=False)
            print(external_api_response)
            if external_api_response.status_code == 200:
                # Create the final Dialogflow response
                response_data = {
                    'fulfillmentMessages': [
                        {'text': {'text': ["Data Update Successfully"]}},
                        {
                            'payload': {
                                'richContent': [
                                    [{'type': 'chips', 'options': [
                                        {'text': 'View'},
                                        {'text': 'Try Another Request ID', 'intent': 'bookingtransfer'}
                                    ]}]
                                ]
                            }
                        }
                    ]
                }
                self.logger.info(f"Data Updated Successfully {requestids} {response_data}")
                return response_data


            else:
                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [f'Please Try Again. Status code: {external_api_response.status_code}']}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Main Menu'},
                                                        {'text': 'Try Again-Cost Price','intent': 'costprice'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                                        ]
                                }
                self.logger.info(f"Data  Not Updated {requestids} {response_data}")
                return (response_data)

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return (response_data)

    

    def handle_all_edit_intent(self, request_data):
        try:
            dialogflow_params = request_data.get('queryResult', {})
            token_context = next(
                (context for context in request_data.get('queryResult', {}).get('outputContexts', []) if 'token-context' in context.get('name', '')),
                {}
            )
            token = token_context.get('parameters', {}).get('token', None)

            request_id_context = next(
                (context for context in request_data.get('queryResult', {}).get('outputContexts', []) if 'request_id' in context.get('name', '')),
                {}
            )
            requestids = request_id_context.get('parameters', {}).get('request_id', None)
            print("request_id_context", request_id_context)
            print('requestids', requestids)
            assignmentid ="1040"
            assignment_id = int(dialogflow_params.get('parameters', {}).get('assignmentid', 0))  
            transfertype = str(dialogflow_params.get('parameters', {}).get('transfertype', 0))
            costprice = int(dialogflow_params.get('parameters', {}).get('costprice', 0))
            conformationno = int(dialogflow_params.get('parameters', {}).get('conformationno', 0))
            status = str(dialogflow_params.get('parameters', {}).get('status', 0))
            overridecost = int(dialogflow_params.get('parameters', {}).get('overridecost', 0))
            totalsalevalue = int(dialogflow_params.get('parameters', {}).get('totalsalevalue', 0))
            drivername = str(dialogflow_params.get('parameters', {}).get('drivername', 0))
            starttime_str = dialogflow_params.get('parameters', {}).get('starttime', '2023-11-15T12:00:00+06:00')
            # Parse ISO 8601 formatted string
            starttime = datetime.fromisoformat(starttime_str)
            # Convert datetime object to string
            starttime_str = starttime.strftime('%Y-%m-%d %H:%M:%S')
            endtime_str = dialogflow_params.get('parameters', {}).get('endtime', '2023-11-15T12:00:00+06:00')
            # Parse ISO 8601 formatted string
            endtime = datetime.fromisoformat(endtime_str)
            # Convert datetime object to string
            endtime_str = endtime.strftime('%Y-%m-%d %H:%M:%S')
            remarks = str(dialogflow_params.get('parameters', {}).get('remarks', 0))
            complimentaryfromsupplier = str(dialogflow_params.get('parameters', {}).get('complimentaryfromsupplier', 0))
            parkingfee = float(dialogflow_params.get('parameters', {}).get('parkingfee', 0))
            total_cost_price = float(dialogflow_params.get('parameters', {}).get('totalcostprice', 0))
            mode = "Edit"

            external_api_url = 'http://150.242.13.125:9092/costprice/' 
            external_api_data = {'requestids': requestids, 'transfertype': transfertype, 'assigntype': 'ARRIVAL', 'partycode': 'OWN TRANSPORT', 'remarks': remarks, 'confno': conformationno, 'assign_status': status, 'costprice': costprice, 'overridecost': overridecost, 'totalsalevalue': totalsalevalue, 'vehicleno': '', 'drivercode': '', 'drivername': drivername, 'drivertel1': '', 'drivertel2': '', 'starttime': starttime_str, 'endtime': endtime_str, 'complimentaryfromsupplier': complimentaryfromsupplier, 'vehiclemaxpax': '0', 'overridemaxpax': '0', 'adddate': '', 'adduser': '', 'moddate': '2023/11/27', 'moduser': 'Sys Admin', 'cartype': '000001', 'sectorgroupcode': '000001','costcurrcode':'', 'mode': mode, 'assignmentid': assignmentid, 'ServiceType': 'TRANSFER', 'salevalue': 30.000, 'parkingfee': parkingfee, 'totalcostprice': total_cost_price}     
            print('external_api_data', external_api_data)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            }

            external_api_response = requests.put(external_api_url, json=external_api_data, headers=headers, verify=False)
            print(external_api_response)
            if external_api_response.status_code == 200:
                # Create the final Dialogflow response
                response_data = {
                    'fulfillmentMessages': [
                        {'text': {'text': ["Data Update Successfully"]}},
                        {
                            'payload': {
                                'richContent': [
                                    [{'type': 'chips', 'options': [
                                        {'text': 'View'},
                                        {'text': 'Try Another Request ID', 'intent': 'bookingtransfer'}
                                    ]}]
                                ]
                            }
                        }
                    ]
                }
                self.logger.info(f"Data Updated Successfully {requestids} {response_data}")
                return response_data


            else:
                response_data = {
                                'fulfillmentMessages': [
                                    {'text': {'text': [f'Please Try Again. Status code: {external_api_response.status_code}']}},
                                    {
                                        'payload': {
                                            'richContent': [
                                                [
                                                    {'type': 'chips', 'options': [
                                                        {'text': 'Main Menu'},
                                                        {'text': 'Try Again-Cost Price','intent': 'costprice'}
                                                    ]}
                                                ]
                                            ]
                                        }
                                    }
                                                        ]
                                }
                self.logger.info(f"Data  Not Updated {requestids} {response_data}")
                return (response_data)

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return (response_data)




    def handle_Main_menu_intent(self, request_data):
        try:
            # Create the final Dialogflow response
            response_data = {
                "fulfillmentMessages": [
                    {
                        'text': {
                            'text': [
                                f"What do you want to access?"
                            ]
                        }
                    },
                    {
                        "payload": {
                            "richContent": [
                                [
                                    {
                                        "type": "chips",
                                        "options": [
                                            {"text": "I want to see Booking List"},
                                            {"text": "Booking List- Request ID"},
                                            {"text": "Booking Details"},
                                            {"text": "Update COST Price    "},
                                            {"text": "Update Transfer Assign Detail"},
                                            {"text": "Driver Duty"},
                                            {"text": "Service Details for Email"},
                                            {"text": "Update Prior Time"},
                                            {"text": "Assigntransfers Getcostprice"},
                                            {"text": "Transfers Dashboard Final"},
                                            {"text": "Transfer List"}
                                        ]
                                    }
                                ]
                            ]
                        }
                    }
                ]
            }

            return response_data

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return response_data
        
    def handle_Edit_intent(self, request_data):
        try:
            # Create the final Dialogflow response
            response_data = {
                "fulfillmentMessages": [
                    {
                        'text': {
                            'text': [
                                f"What do you want to Edit?"
                            ]
                        }
                    },
                    {
                        "payload": {
                            "richContent": [
                                [
                                    {
                                        "type": "chips",
                                        "options": [
                                            {"text": "I want to Update the Cost Price"},
                                            {"text": "I want to update the Conformation no."},
                                            {"text": "I want to update the Transfer No"},
                                            {"text": "I want to update the Status"},
                                            {"text": "I want to Update the Driver name"},
                                            {"text": "More"},
                                           
                                        ]
                                    }
                                ]
                            ]
                        }
                    }
                ]
            }
            output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
            print("Output Contexts:", output_contexts)
            return response_data

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return response_data
    

    def handle_more_intent(self, request_data):
        try:
            # Create the final Dialogflow response
            response_data = {
                "fulfillmentMessages": [
                    {
                        'text': {
                            'text': [
                                f"What do you want to Edit?"
                            ]
                        }
                    },
                    {
                        "payload": {
                            "richContent": [
                                [
                                    {
                                        "type": "chips",
                                        "options": [
                                            {"text": "I want to Update the Cost Price"},
                                            {"text": "I want to update the Conformation no."},
                                            {"text": "I want to update the Transfer No"},
                                            {"text": "I want to update the Status"},
                                            {"text": "I want to Update the Driver name"},
                                            {"text": "I want to Update the Override cost"},
                                            {"text": "I want to Update the Start time"},
                                            {"text": "I want to Update the End time"},
                                            {"text": "I want to Update the Remark"},
                                            {"text": "I want to Update the Parking Fee"}
                                        ]
                                    }
                                ]
                            ]
                        }
                    }
                ]
            }
            output_contexts = request_data.get('queryResult', {}).get('outputContexts', [])
            print("Output Contexts:", output_contexts)
            return response_data

        except Exception as e:
            response_data = {'fulfillmentText': f'An error occurred: {str(e)}'}
            self.logger.error(f"Error during data fetch:{str(e)} ")
            return response_data