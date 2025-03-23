# This file contains functions to log status, errors and warnings for debugging purposes.

import datetime

def log(message, message_type='INFO', sub_process=False):
    '''Prints the given message to Blender's console window. This function helps log functions called by this add-on for debugging purposes.'''
    match message_type:
        case 'ERROR':
            error_prefix = "ERROR: "
        case 'WARNING':
            error_prefix = "WARNING: "
        case _:
            error_prefix = ""
    
    logged_message = "[{0}]: {1}{2}".format(datetime.datetime.now(), error_prefix, message)
    
    if sub_process:
        print(logged_message)
    else:
        print(logged_message)

def log_status(message, self, type='ERROR'):
    '''Prints the given message to Blender's console window and displays the message in Blender's status bar.'''
    if type == 'ERROR':
        message = "{0}".format(message)
    log(message)
    self.report({type}, message)