# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from experiments import experiments

def get_referral_rewards(driver):
    '''
    Returns a (invitee credit, invitor credit) tuple.
    '''
    cohort_id = experiments.assign_alternative(driver.auth_user.username, 'referral_rewards')
    if 'default' == cohort_id:
        return ('75.00', '25.00')
    else:
        return ('50.00', '50.00')
