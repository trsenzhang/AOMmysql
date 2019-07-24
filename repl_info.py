# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 17:07:34 2019

@author: mzhang
"""

单列主键
1062
Last_Error: Could not execute Write_rows event on table test.test2; Duplicate entry '1' for key 'PRIMARY', Error_code: 1062; handler error HA_ERR_FOUND_DUPP_KEY; the event's master log mysql-bin.000038, end_log_pos 10802



1032（delete和update）

Last_Error: Could not execute Update_rows event on table test.test; Can't find record in 'test', Error_code: 1032; handler error HA_ERR_KEY_NOT_FOUND; the event's master log mysql-bin.000038, end_log_pos 9268
Last_Error: Could not execute Delete_rows event on table test.test; Can't find record in 'test', Error_code: 1032; handler error HA_ERR_KEY_NOT_FOUND; the event's master log mysql-bin.000038, end_log_pos 8942
 

复合列主键会影响1062
 
1062
Last_Error: Could not execute Write_rows event on table test.test2; Duplicate entry '1-1-1' for key 'PRIMARY', Error_code: 1062; handler error HA_ERR_FOUND_DUPP_KEY; the event's master log mysql-bin.000038, end_log_pos 10802


1032会影响
Last_Error: Could not execute Delete_rows event on table test.test2; Can't find record in 'test2', Error_code: 1032; handler error HA_ERR_KEY_NOT_FOUND; the event's master log mysql-bin.000038, end_log_pos 11147
Last_Error: Could not execute Update_rows event on table test.test2; Can't find record in 'test2', Error_code: 1032; handler error HA_ERR_KEY_NOT_FOUND; the event's master log mysql-bin.000038, end_log_pos 11901